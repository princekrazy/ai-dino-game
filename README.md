# NeuroRun: Gesture Runner

A real-time **AI-powered gesture-controlled endless runner** built with Python, Pygame, OpenCV, and MediaPipe.

Run, jump, and duck using only your **hand gestures via webcam** — no keyboard required.

---

## Play Now

https://princekrazy.itch.io/dino-ai-game

---

## What is this?

NeuroRun is an interactive computer vision game where your webcam becomes the controller.

Instead of pressing keys, you control the character using real-time hand tracking:

- Open hand (5 fingers) → Jump
- Fist (0 fingers) → Duck

The game uses AI-based hand landmark detection to translate your movements into in-game actions instantly.

---

## Preview

![alt text](image.png)

## Features

- Real-time webcam hand tracking
- AI gesture recognition (MediaPipe)
- ️ Fully playable endless runner
- Smooth physics-based movement
- Procedural obstacle generation
- Score + high score tracking
- Instant restart system after crash
- Gesture smoothing for stable input

---

## ️ Built With

- Python 3
- Pygame (game engine)
- OpenCV (webcam processing)
- MediaPipe (Google hand tracking ML model)

---

## How It Works

1. Webcam captures live video feed
2. MediaPipe detects 21 hand landmarks
3. Finger positions are analyzed
4. Gestures are classified in real time
5. Game reacts instantly inside Pygame loop

This creates a full **real-time AI interaction loop**:

> Camera → AI Vision → Gesture → Game Action

---

## Controls

| Gesture   | Action |
| --------- | ------ |
| Open hand | Jump   |
| Fist      | Duck   |

---

## Why this project matters

This project goes beyond a simple game.

It demonstrates:

- Real-time computer vision systems
- Human-computer interaction (HCI)
- AI-driven input mapping
- Game loop + sensor fusion design

It turns a webcam into a controller — showing how AI can redefine interaction systems.

---

## Challenges solved

- Reducing gesture noise using buffering system
- Handling real-time frame processing delays
- Syncing AI inference with game loop timing
- Optimizing performance for live webcam input

---

## Future Improvements

- Voice control integration (speech commands)
- Custom-trained gesture model
- Multiple difficulty levels
- Sound effects + animations
- Mobile version (touch + camera hybrid)

---

## ‍ Author

Built by **Prince**

Focused on:

- Computer Vision
- AI systems
- Game development
- Human-computer interaction

---

## License

Free to use for learning and personal projects.
