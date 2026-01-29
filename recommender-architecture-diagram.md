# Recommender System Architecture

## Architecture Diagram

```mermaid
graph LR
    subgraph "Input Data Sources"
        Users[Users Table<br/>Demographics]
        Items[Product Items Table]
        Interactions[Interactions Table<br/>Reviews & Ratings]
    end
    
    subgraph "Processing"
        Operator[ADS Recommender Operator]
    end
    
    subgraph "Model"
        Model[Trained Model<br/>recommender_model.pkl]
    end
    
    subgraph "Deployment"
        API[API Endpoint<br/>Model Deployment]
    end
    
    Users -->|user_id, gender, birth_year<br/>income_level, education<br/>occupation, household_size<br/>marital_status, city, state<br/>total_orders, total_spent<br/>avg_order_value| Operator
    Items -->|product_id, product_name<br/>category, category_name<br/>price, avg_rating<br/>num_reviews, recent_popularity| Operator
    Interactions -->|user_id, product_id<br/>rating, quantity<br/>timestamp| Operator
    
    Operator -->|Training| Model
    Model -->|Deploy| API
    
    style Users fill:#e1f5ff
    style Items fill:#e1f5ff
    style Interactions fill:#e1f5ff
    style Operator fill:#fff4e1
    style Model fill:#e8f5e9
    style API fill:#f3e5f5
```

## Data Flow

1. **Input Tables:**
   - **Users Table**: Contains user demographics and profile information
   - **Product Items Table**: Contains product catalog information
   - **Interactions Table**: Contains user-product interactions (reviews, ratings, purchases)

2. **ADS Recommender Operator**: 
   - Processes the three input tables
   - Trains a collaborative filtering model
   - Generates recommendations for users

3. **Trained Model**: 
   - Saved as `recommender_model.pkl`
   - Contains user-product recommendation mappings with predicted ratings

4. **API Endpoint**: 
   - Deployed model as a REST API
   - Accepts user_id and top_k parameters
   - Returns personalized product recommendations
