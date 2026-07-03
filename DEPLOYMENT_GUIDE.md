# 🚀 ATM Face Recognition System - Deployment Guide

## Prerequisites
- Python 3.8 or higher
- Webcam (for face recognition)
- Trained model (trainer/trainer.yml)

---

## 📋 Installation Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Prepare Your Dataset
- Create a `dataset/` folder with subdirectories for each user (1, 2, 3, etc.)
- Place face images in folders: `dataset/1/`, `dataset/2/`, etc.
- Image naming: `username_1.jpg`, `username_2.jpg`, etc.

### 3. Train the Model
```bash
python train_model.py
```
This creates `trainer/trainer.yml` - the trained face recognition model.

### 4. Verify Project Structure
```
project/
├── accounts.json              (auto-created)
├── app.py                     (Streamlit app)
├── requirements.txt           (dependencies)
├── haarcascade_frontalface_default.xml
├── train_model.py            (training script)
├── atm_system.py             (ATM logic)
├── face_login.py             (face recognition logic)
├── dataset/                  (training images)
│   ├── 1/
│   ├── 2/
│   └── 3/
└── trainer/
    └── trainer.yml           (trained model)
```

---

## ▶️ Running the Application

### Local Deployment
```bash
streamlit run app.py
```

The application will open at: `http://localhost:8501`

### Remote/Server Deployment

#### Option A: Using Streamlit Cloud (Recommended for Public)
1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Select your repository and branch
4. Deploy in 2 minutes

#### Option B: Using Docker (Recommended for Servers)

**Create Dockerfile:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Build and Run:**
```bash
docker build -t atm-system .
docker run -p 8501:8501 --device=/dev/video0 atm-system
```

#### Option C: Ubuntu/Linux Server
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install python3-pip python3-dev libatlas-base-dev libjasper-dev libtiff5 libjasper1 libilmbase23

# Install Python dependencies
pip install -r requirements.txt

# Run with nohup (background process)
nohup streamlit run app.py &
```

---

## 🔒 Security Considerations

1. **PIN Security**: Currently PIN is hardcoded. Use environment variables:
```python
import os
PIN = os.getenv('ATM_PIN', '1234')
```

2. **Account Data**: Encrypt `accounts.json`
```bash
pip install cryptography
```

3. **HTTPS**: Use Streamlit with SSL certificate
```bash
streamlit run app.py --logger.level=debug --server.sslCertFile=cert.pem --server.sslKeyFile=key.pem
```

4. **Database**: Replace JSON with PostgreSQL/MySQL for production

---

## 📊 Features

✅ **Face Recognition Login** - Biometric authentication  
✅ **Check Balance** - View current account balance  
✅ **Deposit Money** - Add funds to account  
✅ **Withdraw Money** - Withdraw funds with balance check  
✅ **Change PIN** - Modify security PIN  
✅ **Persistent Storage** - Account data saved in JSON  
✅ **User-Friendly UI** - Streamlit web interface  

---

## 🐛 Troubleshooting

### "Model file not found"
- Run `python train_model.py` first
- Ensure `trainer/trainer.yml` exists

### "No face detected"
- Ensure good lighting
- Face should be clear and centered
- Keep distance 30-60cm from camera

### "Face not recognized"
- Train with more images per user (10-30 images)
- Ensure training images have good variety of angles
- Check confidence threshold in code (default: 75%)

### Camera not working
- Test camera: `python -c "import cv2; cap = cv2.VideoCapture(0)"`
- Ensure webcam permissions are granted
- Try different USB port

### Streamlit connection issues
- Clear cache: `streamlit cache clear`
- Check port availability: `netstat -an | grep 8501`
- Try different port: `streamlit run app.py --server.port=8502`

---

## 🚀 Performance Optimization

### For High-Traffic Deployment
1. Use **caching** for model loading
2. Implement **connection pooling** for database
3. Use **CDN** for static assets
4. Deploy on **high-performance server** (4+ cores, 8GB+ RAM)

### Recommended Server Specs
- **CPU**: 4 cores minimum
- **RAM**: 8GB minimum
- **Storage**: 50GB SSD
- **GPU**: Optional (for faster face recognition)

---

## 📱 Environment Variables

Create `.env` file:
```
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
ATM_PIN=1234
DATABASE_URL=postgresql://user:pass@localhost/atm_db
```

Load in app.py:
```python
from dotenv import load_dotenv
import os
load_dotenv()
```

---

## 📞 Support & Updates

For issues or improvements:
1. Check logs: `streamlit run app.py --logger.level=debug`
2. Test locally first before deploying
3. Keep libraries updated: `pip install --upgrade streamlit opencv-python numpy pillow`

---

## 🎯 Next Steps

1. ✅ Install dependencies
2. ✅ Train the model
3. ✅ Run locally: `streamlit run app.py`
4. ✅ Deploy to cloud/server
5. ✅ Monitor and optimize performance

**Enjoy your ATM System! 🏧**
