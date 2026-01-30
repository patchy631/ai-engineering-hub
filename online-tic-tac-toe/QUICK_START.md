# ⚡ Quick Start Guide - Get Your Game Live in 10 Minutes

## Step 1: Firebase Setup (5 min)

1. **Create project**: [console.firebase.google.com](https://console.firebase.google.com/) → "Add project"

2. **Enable Database**:
   - Build → Realtime Database → Create Database
   - Start in **test mode**
   - Enable

3. **Set Rules** (in Rules tab):
   ```json
   {
     "rules": {
       "rooms": {
         "$roomId": {
           ".read": true,
           ".write": true
         }
       }
     }
   }
   ```

4. **Get Config**:
   - Project Settings (gear icon) → Your apps → Web (`</>`)
   - Copy `firebaseConfig`

5. **Update game.js**:
   - Replace lines 7-14 with your config

## Step 2: Deploy (3 min)

### Option A: Vercel (Recommended)
```bash
npm i -g vercel
cd online-tic-tac-toe
vercel
```
✅ Done! Copy the URL

### Option B: Netlify
1. Drag folder to [app.netlify.com/drop](https://app.netlify.com/drop)
2. ✅ Done! Copy the URL

### Option C: Local Testing
```bash
python3 -m http.server 8000
# Open http://localhost:8000
```

## Step 3: Play! 🎮

1. Visit your URL
2. Create Game → Share link
3. Friend joins → Play!

---

## Troubleshooting

**"Firebase not configured"**
→ Update `game.js` with your Firebase config

**Opponent can't join**
→ Check Firebase Rules are set correctly

**Not deploying**
→ Make sure you're in the `online-tic-tac-toe` directory

---

**Need help?** See full [README.md](README.md)

**Total time**: ~10 minutes
**Total cost**: $0 (Free tier)
