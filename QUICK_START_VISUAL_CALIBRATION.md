# 🎯 Quick Start: 3D Visual Calibration

## ✅ Where to Find It

### **Option 1: From Calibration Page** 
1. Start server:
   ```bash
   cd /Users/sepehrmortazavi/Desktop/robotics_app
   python manage.py runserver 8000
   ```

2. Open in browser:
   ```
   http://127.0.0.1:8000/calibrate/
   ```

3. **Look for the PURPLE GRADIENT BUTTON** that says:
   ```
   🎯 Launch Interactive 3D Calibration Guide
   ```

4. Click it!

### **Option 2: Direct URL**
```
http://127.0.0.1:8000/calibrate/visual/
```

---

## 🖼️ What You Should See

### **Top Section: Progress Bar**
- Shows "Step 1 of 10"
- Progress bar (10% filled for step 1)
- Estimated time remaining

### **Left Panel: 3D Viewer**
- **Loading spinner** appears first (says "Loading 3D model...")
- After 3-10 seconds, the **robot arm 3D model** should appear
- Dark blue/purple background
- Interactive controls on top-right:
  - 🔄 Reset View
  - 🔲 Wireframe
  - ⊞ Grid

### **Right Panel: Instructions**
- Step title: "Power On & Connection"
- Description text
- Numbered instructions (1, 2, 3, 4)
- Target joint positions in a grid
- "Complete Step" button at bottom

### **Bottom: All Steps Overview**
- Grid showing all 10 calibration steps
- Step 1 is highlighted (blue border)
- Other steps are greyed out

---

## 🔧 If Model Doesn't Load

### **Check Browser Console**
1. Right-click on the page → "Inspect"  
2. Click "Console" tab
3. Look for any RED error messages
4. Common issues:

**If you see "Failed to load module script":**
- Your browser doesn't support `importmap`
- Solution: Use Chrome 89+, Firefox 108+, or Safari 16.4+

**If you see "CORS error" or "Failed to fetch":**
- GitHub is blocking the STL file
- Check your internet connection
- Try again in a few minutes

**If you see "THREE is not defined":**
- JavaScript modules didn't load
- Refresh the page (Cmd+R or Ctrl+R)

### **Try These Fixes**

**1. Hard Refresh:**
```
Mac: Cmd + Shift + R
Windows/Linux: Ctrl + Shift + F5
```

**2. Clear Cache:**
- Chrome: Settings → Privacy → Clear browsing data
- Select "Cached images and files"
- Click "Clear data"

**3. Use Different Browser:**
- Chrome (recommended)
- Firefox
- Safari (macOS only)

**4. Check Network:**
```bash
# Test if STL file is accessible
curl -I https://raw.githubusercontent.com/TheRobotStudio/SO-ARM100/main/STL/SO101/Individual/SO101%20Assembly.stl
```

Should return: `HTTP/2 200`

---

## 🎮 How to Use the 3D Viewer

### **Mouse Controls**
- **Left Click + Drag**: Rotate the camera around the model
- **Right Click + Drag**: Pan/move the camera sideways  
- **Scroll Wheel**: Zoom in/out
- **Middle Click + Drag**: Pan (alternative)

### **Button Controls** (top-right corner)
1. **Reset View** 🔄
   - Returns camera to default position for current step
   - Use this if you get lost or model goes off-screen

2. **Wireframe** 🔲
   - Toggles between solid model and wireframe view
   - Wireframe shows the 3D mesh structure
   - Useful for seeing internal details

3. **Grid** ⊞
   - Shows/hides the floor grid
   - Grid helps with spatial orientation

### **Navigation Through Steps**

**Complete Current Step:**
1. Read the instructions
2. Follow the steps
3. Click "Complete Step" button
4. **Automatically advances to Step 2**

**Jump to Specific Step:**
1. Scroll down to "All Calibration Steps" section
2. Click any step card (e.g., "Step 5: Shoulder Lift")
3. **Instantly jump to that step**

**Go Back:**
- Click "Previous Step" button (only shows if not on Step 1)

---

## 📋 10 Calibration Steps Overview

| Step | Title | What You'll See |
|------|-------|----------------|
| **1** | Power On & Connection | Neutral position (all joints at 0°) |
| **2** | Zero Position | Model from top view |
| **3** | Synchronization Check | All joints at 45°, side view |
| **4** | Base Rotation | Base rotated 180°, top view |
| **5** | Shoulder Lift | Shoulder up 180°, side view |
| **6** | Elbow Flex | Elbow bent 180°, side view |
| **7** | Wrist Calibration | Wrist joints at 90°, close-up |
| **8** | Gripper Test | Gripper fully open (180°), zoomed in |
| **9** | Complex Movement | Multi-joint position, diagonal view |
| **10** | Verification | Return to neutral, front view |

---

## ⚡ Troubleshooting Quick Reference

| Problem | Solution |
|---------|----------|
| **Page shows only text, no 3D** | Model is loading—wait 5-10 seconds |
| **Stuck on "Loading 3D model..."** | Check console for errors, refresh page |
| **Model is black/invisible** | Lights didn't initialize—refresh page |
| **Can't rotate/zoom** | Controls didn't load—hard refresh (Cmd+Shift+R) |
| **"Complete Step" doesn't work** | Check browser console, might be JavaScript error |
| **Button not visible on calibrate page** | Server needs restart: `Ctrl+C`, then run `python manage.py runserver 8000` |

---

## 🚀 Expected Performance

### **Loading Times**
- **Page Load**: < 1 second
- **STL Model Download**: 3-10 seconds (depends on internet speed)
- **Model Parsing**: 1-2 seconds
- **Total**: ~5-15 seconds until interactive

### **Performance**
- **Frame Rate**: 60 FPS on modern hardware
- **Model Size**: ~2-5 MB
- **Controls**: Instant response to mouse input

### **Browser Requirements**
- ✅ Chrome 89+ (recommended)
- ✅ Firefox 108+
- ✅ Safari 16.4+
- ✅ Edge 89+
- ❌ Internet Explorer (not supported)

---

## 📸 Visual Guide

### **What the Button Looks Like** (on /calibrate/ page)

```
╔══════════════════════════════════════════════════════╗
║                                                      ║
║   ★  3D Visual Calibration Guide  ★                ║
║                                                      ║
║   Experience an interactive step-by-step            ║
║   calibration guide with real-time 3D               ║
║   visualization                                      ║
║                                                      ║
║   ┌─────────┐ ┌─────────┐ ┌─────────┐             ║
║   │   10    │ │   3D    │ │    ✓    │             ║
║   │ Guided  │ │  STL    │ │  Step   │             ║
║   │  Steps  │ │  Model  │ │ by Step │             ║
║   └─────────┘ └─────────┘ └─────────┘             ║
║                                                      ║
║   [Launch Interactive 3D Calibration Guide →]      ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
    (Purple to pink gradient background)
```

### **What the 3D Page Looks Like**

```
┌────────────────────────────────────────────────────────────┐
│  3D Visual Calibration                                      │
├────────────────────────────────────────────────────────────┤
│  Progress: Step 1 of 10  ▓▓░░░░░░░░  10%                 │
│  ⏱ Estimated time: 30 seconds                              │
├──────────────────────────┬─────────────────────────────────┤
│                          │  📝 Step 1: Power On            │
│    3D MODEL HERE         │                                 │
│                          │  Ensure both robot arms are... │
│   [Robot Arm Rotating]   │                                 │
│                          │  Instructions:                  │
│   Controls:              │  1. Connect USB cables          │
│   [🔄 Reset View]       │  2. Power on leader arm         │
│   [🔲 Wireframe]        │  3. Power on follower arm       │
│   [⊞ Grid]              │  4. Verify LED indicators       │
│                          │                                 │
│                          │  Joint Positions:               │
│                          │  J1: 0°  J2: 0°  J3: 0°        │
│                          │  J4: 0°  J5: 0°  J6: 0°        │
│                          │                                 │
│                          │  [← Previous] [Complete Step →]│
└──────────────────────────┴─────────────────────────────────┘
│                 All Calibration Steps                       │
│  [✓Step 1] [Step 2] [Step 3] [Step 4] [Step 5]...         │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Success Checklist

After opening the page, you should see:

- ✅ Page loads with no 404 errors
- ✅ Progress bar at the top
- ✅ Loading spinner appears in 3D viewer area
- ✅ After 5-10 seconds, **robot arm 3D model appears**
- ✅ Model is blue/purple colored
- ✅ You can **drag to rotate** the model
- ✅ **Scroll to zoom** works
- ✅ Control buttons (Reset/Wireframe/Grid) are visible
- ✅ Instructions panel shows "Step 1: Power On & Connection"
- ✅ Joint position grid shows all 0°
- ✅ "Complete Step" button is clickable
- ✅ Bottom grid shows all 10 steps

**If ALL checkmarks are green** → Success! ✨  
**If ANY are missing** → Check troubleshooting section above

---

## 📞 Need Help?

1. **Check Browser Console** (F12 or Cmd+Option+I)
   - Look for RED errors
   - Screenshot them if you see any

2. **Check Server Terminal**
   - Look for any Python errors
   - Note the exact error message

3. **Verify Server is Running**
   ```bash
   lsof -ti:8000
   ```
   Should return a process ID number

4. **Test Direct Access**
   ```bash
   curl http://127.0.0.1:8000/calibrate/visual/
   ```
   Should return HTML (lots of text)

---

**Good luck! The 3D model should be spinning in your browser now! 🤖🎉**
