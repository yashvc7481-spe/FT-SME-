# CyberGuard SME - Deployment Guide

This guide walks you through deploying **CyberGuard SME** using the standard production split:
- **Backend API**: Deployed on **Render** (or **Railway**) with production Gunicorn WSGI.
- **Frontend**: Deployed on **Vercel** with global CDN edge delivery and dynamic API rewrites.

---

## 📋 Pre-Deployment Summary

All configuration files have been created in the repository:
- `backend/Procfile` & `render.yaml`: Automated build and launch configuration for Render.
- `backend/Dockerfile`: Container configuration for Railway, Render, Fly.io, or VPS.
- `vercel.json` & `frontend/vercel.json`: Vercel routing rules and `/api` proxy rewrites.
- `frontend/js/config.js`: Central frontend API configuration.

---

## Part 1: Push Project to GitHub

1. Create a new GitHub repository (e.g. `cyberguard-sme`) at [github.com/new](https://github.com/new).
2. Connect your local repository and push:
```bash
git remote add origin https://github.com/<YOUR_USERNAME>/cyberguard-sme.git
git branch -M main
git push -u origin main
```

---

## Part 2: Deploy Backend to Render

### Option A: 1-Click Blueprint (Fastest)
1. Log in to [dashboard.render.com](https://dashboard.render.com).
2. Click **New +** → **Blueprint**.
3. Select your `cyberguard-sme` repository.
4. Render will automatically read `render.yaml` and configure:
   - **Environment**: Python
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --workers=2 --threads=4 --timeout=120 --bind=0.0.0.0:$PORT "app:app"`
5. Click **Apply**.
6. Once deployed, copy your backend URL (e.g., `https://cyberguard-sme-backend.onrender.com`).

### Option B: Manual Web Service
1. On Render, click **New +** → **Web Service**.
2. Connect your repository.
3. Configure settings:
   - **Name**: `cyberguard-backend`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --workers=2 --threads=4 --timeout=120 --bind=0.0.0.0:$PORT "app:app"`
4. In **Environment Variables**, add:
   - `APP_SECRET`: *(A random secure string)*
   - `FRONTEND_ORIGIN`: `*` (or your Vercel domain)
5. Click **Create Web Service**.

---

## Part 3: Deploy Frontend to Vercel

1. Log in to [vercel.com](https://vercel.com) and click **Add New...** → **Project**.
2. Import your `cyberguard-sme` GitHub repository.
3. In **Project Configuration**:
   - **Framework Preset**: `Other`
   - **Root Directory**: `./` (or select `frontend`)
4. In `vercel.json` (or via Vercel Rewrites), make sure the destination points to your Render backend URL:
```json
{
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "https://cyberguard-sme-backend.onrender.com/api/$1"
    }
  ]
}
```
5. Click **Deploy**.
6. Your site is now live at `https://your-project.vercel.app`!

---

## Part 4: Alternative Backend Deployment on Railway

1. Go to [railway.app](https://railway.app) and click **New Project** → **Deploy from GitHub repo**.
2. Select `cyberguard-sme`.
3. In **Settings** → **Root Directory**, set `/backend`.
4. Railway will automatically detect the `Dockerfile` or `Procfile` and deploy your service.
5. In **Variables**, add:
   - `PORT`: `5000`
   - `APP_SECRET`: *(random secret)*
6. In **Settings** → **Networking**, click **Generate Domain** to get your public backend URL.
