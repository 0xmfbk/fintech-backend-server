# Fintech Backend Server

A Python FastAPI backend server for managing financial accounts data with Supabase integration.

## 🚀 Features

- **Account Management**: Fetch and store customer account data from external APIs
- **FastAPI Framework**: Modern, fast web framework for building APIs
- **Supabase Integration**: Real-time database with PostgreSQL backend
- **External API Integration**: Fetch account data from financial institutions
- **RESTful API**: Clean, documented API endpoints

## 📁 Project Structure

```
├── accounts_manager.py      # Main FastAPI application with routes
├── accounts_fetcher.py      # External API client for fetching accounts
├── main.py                  # Application entry point
├── supabase_client.py       # Supabase database connection
├── supabase_schema.sql      # Database schema for accounts
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.8+
- Supabase account and project
- External API credentials

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Python_Backend_Server
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   # For production
   pip install -r requirements.txt
   
   # For development (includes testing tools)
   pip install -r requirements-dev.txt
   
   # For minimal production deployment
   pip install -r requirements-prod.txt
   ```

4. **Set up environment variables**
   Create a `.env` file with:
   ```env
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_anon_key
   ```
   
   Note: The external API uses header-based authentication, not API keys.

5. **Set up database**
   - Create a Supabase project
   - Run the SQL commands from `supabase_schema.sql` in your Supabase SQL editor

6. **Run the application**
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Available Endpoints

- `GET /fetch-accounts` - Fetch and store account data from external API
- `GET /accounts` - Retrieve stored account data
- `GET /health` - Health check endpoint

## 🚀 Deployment

### Git Configuration

This project includes `.gitattributes` to handle line endings consistently across different operating systems. If you encounter line ending warnings, they will be automatically resolved.

### Render Deployment

This project is configured for deployment on Render:

1. **Connect your GitHub repository** to Render
2. **Create a new Web Service**
3. **Configure the service**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**: Add your environment variables in Render dashboard

### Environment Variables for Production

Set these in your Render dashboard:
- `SUPABASE_URL`
- `SUPABASE_KEY`

Note: The external API uses header-based authentication, so no API key is needed.

## 🔧 Configuration

### Database Schema

The `supabase_schema.sql` file contains the necessary database tables:

- `accounts` - Stores customer account information
- `account_balances` - Stores account balance history

### External API Integration

The system integrates with external financial APIs to fetch account data including:
- Bank names
- Account status
- Balance amounts
- Account types

## 📊 Monitoring

- **Health Check**: `GET /health` endpoint for monitoring
- **Logs**: Check Render logs for application monitoring
- **Database**: Monitor Supabase dashboard for database performance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the API documentation at `/docs` endpoint
- Review the Supabase documentation for database queries

## 🔗 Links

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Supabase Documentation](https://supabase.com/docs)
- [Render Documentation](https://render.com/docs) 