# Marketplace Platform API

This repository contains the back-end code for a mobile marketplace app for college students to buy and sell goods within their campus community. It includes a database schema and an API for managing users, goods, transactions, and ratings.

## API Specification

https://docs.google.com/document/d/1pCBlVOewwkyrxgJmz6XI9MwRWVub3fd3NoVURZJ97ZY/edit?usp=sharing

## Database Models

### User

- Unique ID
- Name
- NetID
- Rating
- Goods
- Transactions (both as buyer and as seller)

### Good

- Unique ID
- Name
- Image URL (more info below)
- Price
- Seller ID

### Transaction

- Unique ID
- Good ID
- Amount (in cents)
- Rating
- Timestamp
- Buyer
- Seller

## API Routes

- POST /api/users/ - registers a new user
- GET /api/users/{id}/ - retrieves a user's public profile information
- GET /api/users/{id}/goods/ - retrieves all posted goods for a specific user
- GET /api/users/{id}/transactions/ - retrieves the transaction history of a user
- GET /api/users/{id}/rating/ - retrieves the rating for a user
- DELETE /api/users/{id}/ - deletes a user and associated data
- PATCH /api/users/{id}/ - updates the specified user's name

- POST /api/goods/ - creates a new good listing
- GET /api/goods/ - retrieves a list of all goods
- GET /api/goods/{id}/ - retrieves information about a specific good
- DELETE /api/goods/{id}/ - deletes a specific good
- PATCH /api/goods/{id}/ - updates the name/price of a good

- POST /api/transactions/ - creates a new transaction record
- PATCH /api/transactions/{transaction_id}/ - updates rating for the seller in a specific transaction

## Image Storage & Deployment

Each good has one associated image, and such images are stored in an Amazon S3 bucket. This backend is hosted on Google Cloud at http://34.86.134.191/.
