/**
 * OCI Model Deployment API client
 *
 * - Authenticates using OCI config + API key (manual signing compatible with Node.js 22)
 * - Invokes existing OCI Data Science model deployments (product + basket recommenders)
 * - Used by Express routes as a thin wrapper around the OCI predict endpoints
 */

import * as crypto from "crypto";
import * as fs from "fs";
import * as path from "path";
import * as os from "os";

interface OciConfig {
  tenancy: string;
  user: string;
  fingerprint: string;
  keyFile: string;
  region: string;
}

let cachedConfig: OciConfig | null = null;
let cachedPrivateKey: string | null = null;

/**
 * Parse OCI config file
 * Checks for .oci/config in project root first, then falls back to ~/.oci/config
 */
function readOciConfig(): OciConfig {
  if (cachedConfig) {
    return cachedConfig;
  }

  // Check for OCI_CONFIG_FILE environment variable first
  let configPath = process.env.OCI_CONFIG_FILE;
  
  if (!configPath) {
    // Check project root .oci directory (for docker/local consistency)
    const projectOciPath = path.join(process.cwd(), ".oci", "config");
    if (fs.existsSync(projectOciPath)) {
      configPath = projectOciPath;
    } else {
      // Fall back to user home directory
      configPath = path.join(os.homedir(), ".oci", "config");
    }
  }

  if (!fs.existsSync(configPath)) {
    throw new Error(
      `OCI config file not found. Checked:\n` +
      `1. Project root: ${path.join(process.cwd(), ".oci", "config")}\n` +
      `2. Home directory: ${path.join(os.homedir(), ".oci", "config")}\n` +
      `3. OCI_CONFIG_FILE env var: ${process.env.OCI_CONFIG_FILE || "(not set)"}`
    );
  }

  const configContent = fs.readFileSync(configPath, "utf8");
  const config: Partial<OciConfig> = {};

  const configDir = path.dirname(configPath);

  for (const line of configContent.split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#") || trimmed.startsWith("[")) {
      continue;
    }

    const [key, ...valueParts] = trimmed.split("=");
    const value = valueParts.join("=").trim();

    if (key && value) {
      const cleanKey = key.trim();
      let cleanValue = value.replace(/^["']|["']$/g, "").trim();

      if (cleanKey === "user") config.user = cleanValue;
      else if (cleanKey === "tenancy") config.tenancy = cleanValue;
      else if (cleanKey === "fingerprint") config.fingerprint = cleanValue;
      else if (cleanKey === "key_file") {
        // Resolve key file path relative to config directory
        if (cleanValue.startsWith("~")) {
          cleanValue = cleanValue.replace("~", os.homedir());
        } else if (!path.isAbsolute(cleanValue)) {
          // Relative path - resolve relative to config directory
          cleanValue = path.resolve(configDir, cleanValue);
        }
        config.keyFile = cleanValue;
      }
      else if (cleanKey === "region") config.region = cleanValue;
    }
  }

  if (!config.user || !config.tenancy || !config.fingerprint || !config.keyFile) {
    throw new Error("OCI config is missing required fields: user, tenancy, fingerprint, key_file");
  }

  cachedConfig = config as OciConfig;
  return cachedConfig;
}

/**
 * Read private key from file
 */
function readPrivateKey(keyFilePath: string): string {
  if (cachedPrivateKey) {
    return cachedPrivateKey;
  }

  if (!fs.existsSync(keyFilePath)) {
    throw new Error(`Private key file not found at ${keyFilePath}`);
  }

  cachedPrivateKey = fs.readFileSync(keyFilePath, "utf8");
  return cachedPrivateKey;
}

/**
 * Generate OCI request signature
 */
function signRequest(
  method: string,
  path: string,
  host: string,
  body: string,
  config: OciConfig,
  privateKey: string
): Record<string, string> {
  const date = new Date().toUTCString();
  const bodyHash = crypto.createHash("sha256").update(body).digest("base64");

  // Headers to sign
  const headersToSign = [
    `(request-target): ${method.toLowerCase()} ${path}`,
    `host: ${host}`,
    `date: ${date}`,
    `x-content-sha256: ${bodyHash}`,
    `content-type: application/json`,
    `content-length: ${Buffer.byteLength(body, "utf8")}`,
  ];

  const signingString = headersToSign.join("\n");

  // Sign using RSA-SHA256
  const sign = crypto.createSign("RSA-SHA256");
  sign.update(signingString);
  const signature = sign.sign(privateKey, "base64");

  const keyId = `${config.tenancy}/${config.user}/${config.fingerprint}`;
  const headers = "(request-target) host date x-content-sha256 content-type content-length";
  const authorization = `Signature version="1",keyId="${keyId}",algorithm="rsa-sha256",headers="${headers}",signature="${signature}"`;

  return {
    date,
    "x-content-sha256": bodyHash,
    "content-type": "application/json",
    "content-length": Buffer.byteLength(body, "utf8").toString(),
    host,
    authorization,
  };
}

/**
 * Low-level helper to POST JSON to a signed OCI model deployment endpoint.
 *
 * @param endpoint Base model deployment URL (without /predict suffix)
 * @param payload  JSON-serializable request body
 */
async function signedPost(endpoint: string, payload: unknown): Promise<any> {
  try {
    // Read OCI config and private key
    const config = readOciConfig();
    const privateKey = readPrivateKey(config.keyFile);

    // Model deployments expect POST to {endpoint}/predict
    const url = endpoint.endsWith("/predict") ? endpoint : `${endpoint}/predict`;
    const body = JSON.stringify(payload ?? {});

    // Parse URL
    const urlObj = new URL(url);
    const host = urlObj.host;
    const path = urlObj.pathname + (urlObj.search || "");

    // Generate OCI signature
    const headers = signRequest("POST", path, host, body, config, privateKey);

    // Make the request
    const response = await fetch(url, {
      method: "POST",
      headers,
      body,
    });

    if (!response.ok) {
      const text = await response.text().catch(() => "");
      throw new Error(
        `OCI model deployment error: ${response.status} ${response.statusText}${
          text ? ` - ${text}` : ""
        }`
      );
    }

    return response.json();
  } catch (error: any) {
    if (error.message?.includes("model deployment error")) {
      throw error;
    }
    throw new Error(
      `Failed to call OCI model deployment: ${error?.message || String(error)}. ` +
      `Please verify:\n` +
      `1. OCI config file exists at ~/.oci/config\n` +
      `2. API key file path in config is correct and file exists\n` +
      `3. API key file has correct permissions (chmod 600)`
    );
  }
}

/**
 * Call the product recommender model deployment for a given user.
 *
 * @param userId User identifier
 * @param topK   Number of recommendations to request (default 10)
 */
export async function predictUserRecs(
  userId: string,
  topK: number = 10
): Promise<any> {
  const endpoint = process.env.OCI_PRODUCT_RECOMMENDER_MODEL_ENDPOINT;
  if (!endpoint) {
    throw new Error(
      "OCI_PRODUCT_RECOMMENDER_MODEL_ENDPOINT is not configured in environment variables"
    );
  }

  const payload = {
    user_id: userId,
    top_k: topK,
  };

  return signedPost(endpoint, payload);
}

/**
 * Call the basket recommender model deployment for a given basket.
 *
 * @param basket Array of product IDs currently in the basket
 * @param topN   Number of association rules / recommendations to request (default 3)
 */
export async function predictBasketRecs(
  basket: string[],
  topN: number = 3
): Promise<any> {
  const endpoint = process.env.OCI_BASKET_RECOMMENDER_MODEL_ENDPOINT;
  if (!endpoint) {
    throw new Error(
      "OCI_BASKET_RECOMMENDER_MODEL_ENDPOINT is not configured in environment variables"
    );
  }

  // Basket model expects {"data": [[...product_ids...]]}
  const payload = {
    data: [basket],
    top_n: topN,
  };

  return signedPost(endpoint, payload);
}

/**
 * Lightweight health check for a given model deployment endpoint.
 *
 * NOTE: This should not be wired to any hot paths; it's intended for
 *       diagnostics or future health endpoints.
 */
export async function testConnection(
  endpointEnvVar: "OCI_PRODUCT_RECOMMENDER_MODEL_ENDPOINT" | "OCI_BASKET_RECOMMENDER_MODEL_ENDPOINT"
): Promise<boolean> {
  try {
    const endpoint = process.env[endpointEnvVar];
    if (!endpoint) {
      return false;
    }

    // Send a minimal payload; model will likely error on semantics, but we
    // only care that the endpoint is reachable and auth works.
    await signedPost(endpoint, {});
    return true;
  } catch (err) {
    console.warn(`OCI model deployment connection test failed for ${endpointEnvVar}:`, (err as any)?.message);
    return false;
  }
}

