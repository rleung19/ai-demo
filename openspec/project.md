# Project Context

## Purpose
AI demo/workshop project for demonstrating AI capabilities and integrations. This is a Next.js application built for the 2026 AI workshop, serving as a demonstration platform for AI features and workflows.

## Tech Stack
- **Framework**: Next.js 16.1.1 (App Router)
- **UI Library**: React 19.2.3
- **Language**: TypeScript 5
- **Styling**: Tailwind CSS 4
- **Fonts**: Geist Sans & Geist Mono (via next/font)
- **Linting**: ESLint 9 with Next.js configs
- **Build Tool**: Next.js built-in bundler

## Project Conventions

### Code Style
- **TypeScript**: Strict mode enabled (`strict: true` in tsconfig.json)
- **Naming**: Follow React/Next.js conventions (PascalCase for components, camelCase for functions/variables)
- **Path Aliases**: Use `@/*` for imports from project root (configured in tsconfig.json)
- **Formatting**: ESLint with Next.js core-web-vitals and TypeScript rules
- **File Extensions**: Use `.tsx` for React components, `.ts` for utilities/types
- **Styling**: Tailwind CSS utility classes with dark mode support via `dark:` prefix

### Architecture Patterns
- **App Router**: Using Next.js App Router architecture (`app/` directory)
- **Server Components**: Default to React Server Components where possible
- **Layout System**: Root layout in `app/layout.tsx` with global styles and fonts
- **Component Organization**: Components organized in `app/` directory following Next.js conventions
- **Type Safety**: Full TypeScript coverage with strict mode for type safety

### Testing Strategy
- Testing strategy not yet established (no test files or testing dependencies found)
- Consider adding Jest/Vitest and React Testing Library for future testing needs

### Git Workflow
- Git workflow conventions not yet documented
- Consider establishing branching strategy (e.g., main/develop, feature branches)
- Consider commit message conventions (e.g., Conventional Commits)

## Domain Context
- This is a demo/workshop project, so flexibility and experimentation are encouraged
- Focus on demonstrating AI capabilities and integrations
- UI should be modern and user-friendly to showcase features effectively

## Important Constraints
- **Next.js Version**: Using Next.js 16.1.1 - be aware of App Router patterns and limitations
- **React Version**: React 19.2.3 - ensure compatibility with Next.js 16
- **TypeScript Strict Mode**: All code must pass strict type checking
- **Browser Support**: Target modern browsers (ES2017+)

## External Dependencies
- **Vercel**: Deployment platform (recommended by Next.js)
- **Google Fonts**: Geist fonts loaded via next/font
- No other external services or APIs currently configured
