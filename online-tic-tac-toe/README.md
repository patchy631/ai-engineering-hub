# 🎮 Online Tic-Tac-Toe

A simple, serverless online multiplayer tic-tac-toe game that you can play with friends anywhere in the world! No accounts required, just create a room and share the link.

## ✨ Features

- 🌐 **Online Multiplayer** - Play with anyone via room codes
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile
- ⚡ **Real-time Updates** - Instant move synchronization
- 💬 **Quick Chat** - Communicate with your opponent
- 🎯 **Simple UI** - Clean, intuitive interface
- 🔒 **No Backend Code** - Serverless architecture using Firebase
- 🚀 **Fast Deployment** - Get a shareable link in minutes

## 🚀 Quick Start

### Prerequisites

1. A Firebase account (free tier works perfectly)
2. A Vercel/Netlify account for hosting (optional but recommended)

### Setup Instructions

#### Step 1: Firebase Setup (5 minutes)

1. **Create Firebase Project**
   - Go to [Firebase Console](https://console.firebase.google.com/)
   - Click "Add project"
   - Enter a project name (e.g., "online-tic-tac-toe")
   - Disable Google Analytics (optional)
   - Click "Create project"

2. **Enable Realtime Database**
   - In your Firebase project, go to "Build" → "Realtime Database"
   - Click "Create Database"
   - Choose a location (closest to your users)
   - Start in **test mode** (for development)
   - Click "Enable"

3. **Configure Database Rules** (Important for security)
   - In Realtime Database, go to "Rules" tab
   - Replace the rules with:
   ```json
   {
     "rules": {
       "rooms": {
         "$roomId": {
           ".read": true,
           ".write": true,
           ".indexOn": ["lastUpdate"]
         }
       }
     }
   }
   ```
   - Click "Publish"

4. **Get Firebase Configuration**
   - Go to Project Settings (gear icon)
   - Scroll down to "Your apps"
   - Click the web icon (`</>`)
   - Register app with a nickname (e.g., "tic-tac-toe-web")
   - Copy the `firebaseConfig` object

5. **Update game.js**
   - Open `game.js`
   - Replace the `firebaseConfig` object at the top with your config:
   ```javascript
   const firebaseConfig = {
       apiKey: "YOUR_ACTUAL_API_KEY",
       authDomain: "your-project.firebaseapp.com",
       databaseURL: "https://your-project-default-rtdb.firebaseio.com",
       projectId: "your-project",
       storageBucket: "your-project.appspot.com",
       messagingSenderId: "123456789",
       appId: "1:123456789:web:abcdef"
   };
   ```

#### Step 2: Test Locally (2 minutes)

```bash
# Navigate to the project directory
cd online-tic-tac-toe

# Start a local server (Python 3)
python3 -m http.server 8000

# Or use Node.js
npx http-server -p 8000

# Or use PHP
php -S localhost:8000
```

Open your browser to:
- `http://localhost:8000`

Test the game by:
1. Creating a room
2. Opening the copied link in another browser/incognito window
3. Playing a few moves

#### Step 3: Deploy to Vercel (3 minutes)

**Option A: Using Vercel CLI (Fastest)**

```bash
# Install Vercel CLI globally
npm i -g vercel

# Deploy (from project directory)
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No
# - What's your project's name? online-tic-tac-toe
# - In which directory is your code located? ./
# - Want to override settings? No

# Get production URL
vercel --prod
```

**Option B: Using Vercel Website**

1. Go to [vercel.com](https://vercel.com)
2. Sign up/login (GitHub account recommended)
3. Click "Add New" → "Project"
4. Import your Git repository (or upload files)
5. Configure:
   - Framework Preset: Other
   - Root Directory: ./
   - Build Command: (leave empty)
   - Output Directory: ./
6. Click "Deploy"
7. Wait ~30 seconds
8. Get your URL: `https://your-project.vercel.app`

**Option C: Deploy to Netlify**

1. Go to [netlify.com](https://netlify.com)
2. Sign up/login
3. Drag and drop the `online-tic-tac-toe` folder
4. Wait ~30 seconds
5. Get your URL: `https://random-name.netlify.app`

#### Step 4: Share & Play! 🎉

1. Visit your deployed URL
2. Click "Create Game"
3. Copy the room link
4. Send to a friend
5. Start playing!

## 📁 Project Structure

```
online-tic-tac-toe/
├── index.html          # Home page (create/join room)
├── game.html           # Game interface
├── style.css           # All styles
├── game.js             # Game logic + Firebase integration
├── package.json        # Project metadata
├── vercel.json         # Vercel configuration
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## 🎮 How to Play

1. **Create a Room**
   - Enter your name
   - Click "Create Room"
   - Share the generated link with your friend

2. **Join a Room**
   - Get the room code from your friend
   - Enter your name and the room code
   - Click "Join Room"

3. **Play**
   - First player (X) goes first
   - Click on empty squares to make your move
   - Win by getting 3 in a row (horizontal, vertical, or diagonal)
   - Use the chat to communicate

4. **New Game**
   - Click "New Game" to reset the board
   - Same room, same players, fresh start

## 🔧 Configuration

### Firebase Database Rules

For **development/testing** (anyone can read/write):
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

For **production** (with basic validation):
```json
{
  "rules": {
    "rooms": {
      "$roomId": {
        ".read": true,
        ".write": true,
        ".validate": "newData.hasChildren(['board', 'currentPlayer', 'players'])",
        "board": {
          ".validate": "newData.val().length === 9"
        },
        "currentPlayer": {
          ".validate": "newData.val() === 'X' || newData.val() === 'O'"
        }
      }
    }
  }
}
```

### Auto-cleanup

The app includes basic client-side cleanup for inactive rooms (1 hour timeout). For better cleanup, consider:

1. **Cloud Functions** (Firebase, paid plan required):
```javascript
// Schedule to run every hour
exports.cleanupOldRooms = functions.pubsub
  .schedule('every 1 hours')
  .onRun(async (context) => {
    const cutoff = Date.now() - (60 * 60 * 1000);
    // Delete rooms older than cutoff
  });
```

2. **Manual cleanup**: Periodically check Firebase Console and delete old rooms

## 🌐 Browser Support

- Chrome/Edge (recommended)
- Firefox
- Safari
- Mobile browsers (iOS Safari, Chrome Mobile)

## ⚠️ Limitations

### Current Implementation:
- ✅ No accounts required
- ✅ Works on any device with a browser
- ✅ Real-time synchronization
- ✅ Free to host and use
- ⚠️ Rooms don't persist forever (auto-cleanup after inactivity)
- ⚠️ No game history or statistics
- ⚠️ Firebase free tier limits:
  - 1GB data transfer/day
  - 10GB storage
  - 100 simultaneous connections
  - (Plenty for personal use!)

### Security Notes:
- Room codes are 6 random characters (not cryptographically secure)
- Anyone with a room code can join
- Data is stored in Firebase (not end-to-end encrypted)
- Don't share sensitive information in chat

## 🛠️ Customization

### Change Colors

Edit `style.css`:
```css
/* Primary gradient */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Change to your colors */
background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 100%);
```

### Add Player Avatars

In `game.html`, replace:
```html
<div class="player-badge">❌</div>
```

With:
```html
<img src="avatar.png" class="player-avatar">
```

### Custom Win Messages

In `game.js`, modify:
```javascript
if (state.winner === mySymbol) {
    statusDiv.textContent = '🎉 You won!';
}
```

## 🐛 Troubleshooting

### "Firebase not configured" error
- Make sure you've replaced `YOUR_API_KEY` in `game.js` with your actual Firebase config
- Check that all Firebase config fields are filled

### Opponent can't join
- Verify the room code is correct
- Check Firebase Database rules allow writes
- Ensure Firebase Realtime Database is enabled

### Moves not syncing
- Check browser console for errors
- Verify Firebase Database URL is correct
- Check internet connection

### Deploy fails on Vercel
- Make sure all files are in the project root
- Check `vercel.json` is present
- Try deploying via Vercel website instead of CLI

## 📊 Cost Estimate

**Firebase Free Tier** (Spark Plan):
- Realtime Database: 1GB storage, 10GB/month transfer
- Hosting: 10GB storage, 360MB/day transfer
- **Estimated capacity**: ~1000 games/day (well within free tier)

**Vercel Free Tier**:
- 100GB bandwidth/month
- Unlimited deployments
- **Cost**: $0/month for typical usage

**Total Monthly Cost**: **$0** 🎉

## 🚀 Advanced Features (Future Ideas)

- [ ] Player rankings/leaderboard
- [ ] Best of 3/5 match mode
- [ ] Custom board sizes (4x4, 5x5)
- [ ] Spectator mode
- [ ] Game replays
- [ ] Player profiles with avatars
- [ ] Sound effects
- [ ] Animations
- [ ] Dark mode
- [ ] Multiple game rooms per session

## 📝 License

MIT License - Feel free to use, modify, and distribute!

## 🤝 Contributing

Found a bug? Want to add a feature? PRs welcome!

## 📞 Support

Having issues? Check:
1. Firebase Console for database errors
2. Browser console for JavaScript errors
3. GitHub Issues for similar problems

## 🎯 Performance Tips

1. **Use Firebase CDN**: Already implemented with ESM imports
2. **Enable caching**: Vercel/Netlify handle this automatically
3. **Optimize images**: Use compressed assets if you add custom graphics
4. **Monitor usage**: Check Firebase Console for quota usage

## 🔐 Security Best Practices

1. **Don't commit Firebase config** to public repos (use environment variables)
2. **Set Firebase rules properly** (see Configuration section)
3. **Implement rate limiting** for production apps
4. **Add CAPTCHA** if you notice abuse
5. **Monitor Firebase logs** for suspicious activity

## 📱 Mobile Tips

- Game is fully responsive
- Touch controls work out of the box
- Add to home screen for app-like experience
- Works offline after initial load (with service worker)

## 🎨 Design Credits

- Icons: System emojis
- Colors: Custom gradient palette
- Layout: CSS Grid + Flexbox
- Font: System font stack

---

**Enjoy your game! 🎮**

Made with ❤️ using Firebase and Vanilla JavaScript

Questions? Open an issue on GitHub!
