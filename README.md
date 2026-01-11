# Wardo 👗

A smart wardrobe management and outfit recommendation system powered by AI and computer vision.

## 🌐 Live Demo
**[https://wardo-8u10.onrender.com](https://wardo-8u10.onrender.com)**

## 📋 Overview

Wardo is an intelligent wardrobe management application that helps users:
- **Manage their wardrobe** - Upload and catalog clothing items
- **Analyze clothing** - Detect color, undertone, and weather suitability using computer vision
- **Get recommendations** - Receive AI-powered outfit suggestions based on occasion and weather
- **Track wear count** - Monitor which items are worn most frequently
- **Personalized styling** - Recommendations based on your skin tone and preferences

## ✨ Features

### 🎨 Smart Color Detection
- Automatic color recognition using OpenCV and HSV color space analysis
- Support for detecting: Black, White, Red, Orange, Yellow, Green, Blue, Purple

### 🌡️ Undertone Analysis
- Cool vs. Warm undertone classification
- Helps match clothing to skin tone for optimal appearance

### 🌤️ Weather & Occasion Matching
- Categorize clothing by weather (hot, cold, rainy, neutral)
- Match outfits to occasions (casual, formal, party, work)

### 👔 Outfit Recommendations
- AI-powered outfit matching based on:
  - Selected piece
  - Occasion type
  - Weather conditions
  - Color harmony

### 📊 Wardrobe Analytics
- Track wear count for each item
- Identify most worn and least worn pieces
- Optimize wardrobe composition

## 🛠️ Tech Stack

### Backend
- **Flask** - Python web framework
- **Flask-CORS** - Cross-origin request handling
- **Flask-SQLAlchemy** - ORM for database management
- **OpenCV** - Computer vision for image processing
- **NumPy** - Numerical computing
- **Gunicorn** - WSGI HTTP Server

### Frontend
- **HTML5** - Structure
- **CSS3** - Styling with responsive design
- **Vanilla JavaScript** - Interactive features

### Database
- **SQLite** - Lightweight relational database

### Deployment
- **Render** - Cloud hosting platform

## 📁 Project Structure

```
wardo/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── render.yaml           # Render deployment config
├── index.html            # Homepage
├── dashboard.html        # User dashboard
├── profile.html          # User profile
├── wardrobe.html         # Wardrobe management
├── stylist.html          # Outfit recommendation engine
├── signin.html           # Authentication
├── signup.html           # Registration
├── styles/               # CSS stylesheets
│   ├── dashboard.css
│   ├── index.css
│   ├── profile.css
│   ├── wardrobe.css
│   ├── stylist.css
│   └── resources/        # Images and fonts
├── uploads/              # User uploaded images
└── instance/             # SQLite database files
```

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/NotKammu/Wardo.git
   cd Wardo
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run locally**
   ```bash
   python app.py
   ```
   Visit `http://localhost:5000` in your browser

## 📦 API Endpoints

### Authentication
- `POST /signin` - User login
- `POST /signup` - User registration

### Wardrobe Management
- `POST /upload` - Upload clothing image
- `GET /wardrobe` - Retrieve all wardrobe items
- `DELETE /delete/<id>` - Delete clothing item
- `POST /wear` - Update wear count

### Styling & Recommendations
- `POST /undertone` - Analyze skin undertone
- `POST /stylist` - Get outfit recommendations
- `POST /match` - Find matching pieces

### Analysis
- `POST /colordetect` - Detect item color
- `GET /health` - API health check

## 👥 Team

| Name | Role |
|------|------|
| **Ganesh** | Full Stack Developer |
| **Adithya** | Full Stack Developer |
| **Naveen** | Full Stack Developer |
| **Sahuban** | Full Stack Developer |

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Repository**: [github.com/NotKammu/Wardo](https://github.com/NotKammu/Wardo)
- **Live App**: [wardo-8u10.onrender.com](https://wardo-8u10.onrender.com)
- **Issues & Support**: [GitHub Issues](https://github.com/NotKammu/Wardo/issues)

## 💡 Future Enhancements

- [ ] Machine learning model for better outfit matching
- [ ] Virtual try-on with AR
- [ ] Social sharing of outfits
- [ ] Clothing price tracking
- [ ] Sustainability metrics
- [ ] Integration with e-commerce for clothing suggestions
- [ ] Mobile app version

---

**Made with ❤️ by the Wardo Team**
 
## 📷 Screenshots

Below are screenshots showing the app UI and an example error page captured during deployment testing.

![Serverless Function Error](ss1.jpeg)

![Personalization Form - Centered](ss2.jpeg)

![Style Input Modal](ss3.jpeg)
