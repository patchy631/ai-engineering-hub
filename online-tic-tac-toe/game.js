// ========================================
// FIREBASE CONFIGURATION
// ========================================
// Replace with your Firebase config from Firebase Console
// See README.md for detailed setup instructions

const firebaseConfig = {
    apiKey: "YOUR_API_KEY",
    authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
    databaseURL: "https://YOUR_PROJECT_ID-default-rtdb.firebaseio.com",
    projectId: "YOUR_PROJECT_ID",
    storageBucket: "YOUR_PROJECT_ID.appspot.com",
    messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
    appId: "YOUR_APP_ID"
};

// ========================================
// CHECK CONFIGURATION
// ========================================
if (firebaseConfig.apiKey === "YOUR_API_KEY") {
    document.getElementById('configNotice').classList.remove('hidden');
    console.error("Firebase not configured! Please update firebaseConfig in game.js");
}

// ========================================
// FIREBASE INITIALIZATION
// ========================================
import { initializeApp } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js';
import { getDatabase, ref, set, onValue, update, remove } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-database.js';

const app = initializeApp(firebaseConfig);
const database = getDatabase(app);

// ========================================
// GAME STATE
// ========================================
const urlParams = new URLSearchParams(window.location.search);
const roomCode = urlParams.get('room');
const playerName = urlParams.get('player');
const isHost = urlParams.get('host') === 'true';

let gameState = {
    board: Array(9).fill(null),
    currentPlayer: 'X',
    players: {},
    gameOver: false,
    winner: null
};

let mySymbol = null;
let opponentSymbol = null;

// ========================================
// DOM ELEMENTS
// ========================================
const cells = document.querySelectorAll('.cell');
const statusDiv = document.getElementById('status');
const roomDisplay = document.getElementById('roomDisplay');
const copyBtn = document.getElementById('copyBtn');
const homeBtn = document.getElementById('homeBtn');
const resetBtn = document.getElementById('resetBtn');
const player1NameDiv = document.getElementById('player1Name');
const player2NameDiv = document.getElementById('player2Name');
const player1Info = document.getElementById('player1Info');
const player2Info = document.getElementById('player2Info');
const gameBoard = document.getElementById('gameBoard');
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');

// ========================================
// INITIALIZATION
// ========================================
roomDisplay.textContent = roomCode;

// Setup room reference
const roomRef = ref(database, `rooms/${roomCode}`);

// Initialize room if host
if (isHost) {
    set(roomRef, {
        board: Array(9).fill(null),
        currentPlayer: 'X',
        players: {
            X: playerName,
            O: null
        },
        gameOver: false,
        winner: null,
        chat: []
    });
    mySymbol = 'X';
    opponentSymbol = 'O';
} else {
    // Join as player O
    mySymbol = 'O';
    opponentSymbol = 'X';

    // Update player O name
    onValue(roomRef, (snapshot) => {
        if (snapshot.exists()) {
            const data = snapshot.val();
            if (!data.players.O) {
                update(roomRef, {
                    'players/O': playerName
                });
            }
        }
    }, { onlyOnce: true });
}

// ========================================
// GAME LOGIC
// ========================================
const winningCombinations = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8], // Rows
    [0, 3, 6], [1, 4, 7], [2, 5, 8], // Columns
    [0, 4, 8], [2, 4, 6]             // Diagonals
];

function checkWinner(board) {
    for (let combo of winningCombinations) {
        const [a, b, c] = combo;
        if (board[a] && board[a] === board[b] && board[a] === board[c]) {
            return { winner: board[a], combo };
        }
    }

    if (board.every(cell => cell !== null)) {
        return { winner: 'draw', combo: null };
    }

    return null;
}

function handleCellClick(index) {
    if (gameState.board[index] || gameState.gameOver) return;
    if (gameState.currentPlayer !== mySymbol) return;

    // Make move
    const newBoard = [...gameState.board];
    newBoard[index] = mySymbol;

    const result = checkWinner(newBoard);
    const nextPlayer = mySymbol === 'X' ? 'O' : 'X';

    const updates = {
        board: newBoard,
        currentPlayer: nextPlayer
    };

    if (result) {
        updates.gameOver = true;
        updates.winner = result.winner;
        if (result.combo) {
            updates.winningCombo = result.combo;
        }
    }

    update(roomRef, updates);
}

function renderBoard(board, winningCombo = null) {
    cells.forEach((cell, index) => {
        const value = board[index];

        if (value === 'X') {
            cell.textContent = '❌';
            cell.classList.add('taken');
        } else if (value === 'O') {
            cell.textContent = '⭕';
            cell.classList.add('taken');
        } else {
            cell.textContent = '';
            cell.classList.remove('taken');
        }

        // Highlight winning cells
        if (winningCombo && winningCombo.includes(index)) {
            cell.classList.add('winning');
        } else {
            cell.classList.remove('winning');
        }
    });
}

function updateStatus(state) {
    const bothPlayersJoined = state.players.X && state.players.O;

    if (!bothPlayersJoined) {
        statusDiv.textContent = 'Waiting for opponent to join...';
        statusDiv.className = 'status waiting';
        gameBoard.classList.add('disabled');
        resetBtn.disabled = true;
        return;
    }

    resetBtn.disabled = false;
    gameBoard.classList.remove('disabled');

    if (state.gameOver) {
        if (state.winner === 'draw') {
            statusDiv.textContent = "It's a draw!";
        } else if (state.winner === mySymbol) {
            statusDiv.textContent = '🎉 You won!';
        } else {
            statusDiv.textContent = '😢 You lost!';
        }
        statusDiv.className = 'status game-over';
        gameBoard.classList.add('disabled');
    } else {
        if (state.currentPlayer === mySymbol) {
            statusDiv.textContent = 'Your turn!';
            statusDiv.className = 'status your-turn';
        } else {
            statusDiv.textContent = "Opponent's turn...";
            statusDiv.className = 'status opponent-turn';
        }
    }

    // Update player highlights
    if (state.currentPlayer === 'X') {
        player1Info.classList.add('active');
        player2Info.classList.remove('active');
    } else {
        player1Info.classList.remove('active');
        player2Info.classList.add('active');
    }
}

function updatePlayerNames(players) {
    player1NameDiv.textContent = players.X || 'Waiting...';
    player2NameDiv.textContent = players.O || 'Waiting...';
}

// ========================================
// CHAT FUNCTIONALITY
// ========================================
function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    onValue(roomRef, (snapshot) => {
        if (snapshot.exists()) {
            const data = snapshot.val();
            const chat = data.chat || [];
            chat.push({
                sender: playerName,
                text: message,
                timestamp: Date.now()
            });

            update(roomRef, { chat });
            chatInput.value = '';
        }
    }, { onlyOnce: true });
}

function renderChat(messages) {
    if (!messages || messages.length === 0) {
        chatMessages.innerHTML = '<div style="text-align: center; color: #999;">No messages yet</div>';
        return;
    }

    chatMessages.innerHTML = messages.map(msg => `
        <div class="chat-message">
            <div class="sender">${msg.sender}</div>
            <div class="text">${msg.text}</div>
        </div>
    `).join('');

    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// ========================================
// EVENT LISTENERS
// ========================================
cells.forEach((cell, index) => {
    cell.addEventListener('click', () => handleCellClick(index));
});

copyBtn.addEventListener('click', () => {
    const link = window.location.href.split('?')[0] + `?room=${roomCode}&player=Friend&host=false`;
    navigator.clipboard.writeText(link).then(() => {
        const originalText = copyBtn.textContent;
        copyBtn.textContent = '✓ Copied!';
        setTimeout(() => {
            copyBtn.textContent = originalText;
        }, 2000);
    });
});

homeBtn.addEventListener('click', () => {
    if (confirm('Are you sure you want to leave the game?')) {
        window.location.href = 'index.html';
    }
});

resetBtn.addEventListener('click', () => {
    update(roomRef, {
        board: Array(9).fill(null),
        currentPlayer: 'X',
        gameOver: false,
        winner: null,
        winningCombo: null
    });
});

sendBtn.addEventListener('click', sendMessage);

chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

// ========================================
// REAL-TIME SYNC
// ========================================
onValue(roomRef, (snapshot) => {
    if (snapshot.exists()) {
        const data = snapshot.val();
        gameState = data;

        renderBoard(data.board, data.winningCombo);
        updateStatus(data);
        updatePlayerNames(data.players);

        if (data.chat) {
            renderChat(data.chat);
        }
    } else {
        statusDiv.textContent = 'Room not found!';
        statusDiv.className = 'status';
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    // Optional: Clean up old rooms
    // This is basic - you might want to implement a more sophisticated cleanup
});

// ========================================
// AUTO-CLEANUP (Optional)
// ========================================
// Remove rooms that are inactive for more than 1 hour
// This would typically be done server-side, but here's a client-side approach
const ROOM_TIMEOUT = 60 * 60 * 1000; // 1 hour

onValue(roomRef, (snapshot) => {
    if (snapshot.exists()) {
        const data = snapshot.val();
        const lastUpdate = data.lastUpdate || Date.now();

        if (Date.now() - lastUpdate > ROOM_TIMEOUT) {
            remove(roomRef);
        } else {
            update(roomRef, { lastUpdate: Date.now() });
        }
    }
}, { onlyOnce: true });

console.log('Game initialized:', { roomCode, playerName, mySymbol });
