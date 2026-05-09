---
title: 'Signals: An Interactive Playground'
subtitle: 'Explore reactive programming by playing with living systems'
date: 2026-04-12
type: interactive-article
style: bret-victor-explorable
topics: [reactive-systems, signals, interactive-learning, visualization]
---

<style>
.interactive-container {
  border: 2px solid #333;
  border-radius: 8px;
  padding: 20px;
  margin: 20px 0;
  background: #f8f9fa;
  font-family: 'Monaco', 'Menlo', monospace;
}

.signal-node {
  display: inline-block;
  padding: 10px 15px;
  margin: 5px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: bold;
}

.signal-source {
  background: #4CAF50;
  color: white;
  border: 3px solid #2E7D32;
}

.signal-source:hover {
  background: #66BB6A;
  transform: scale(1.05);
}

.signal-computed {
  background: #2196F3;
  color: white;
  border: 3px solid #1565C0;
}

.signal-effect {
  background: #FF9800;
  color: white;
  border: 3px solid #EF6C00;
}

.dependency-line {
  stroke: #666;
  stroke-width: 2;
  fill: none;
  marker-end: url(#arrowhead);
}

.dependency-line.active {
  stroke: #f44336;
  stroke-width: 4;
  animation: pulse 0.5s ease-in-out;
}

@keyframes pulse {
  0%, 100% { stroke-width: 2; }
  50% { stroke-width: 6; }
}

.value-display {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 10px 0;
}

.control-panel {
  background: white;
  padding: 15px;
  border-radius: 8px;
  margin: 10px 0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

button {
  background: #673AB7;
  color: white;
  border: none;
  padding: 10px 20px;
  margin: 5px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

button:hover {
  background: #7E57C2;
}

button:active {
  transform: translateY(1px);
}

.slider-container {
  margin: 15px 0;
}

input[type="range"] {
  width: 100%;
  height: 8px;
  border-radius: 4px;
  background: #ddd;
  outline: none;
}

.log-entry {
  padding: 5px 10px;
  margin: 2px 0;
  border-left: 3px solid #673AB7;
  background: white;
  font-size: 12px;
  font-family: monospace;
}

.explanation-box {
  background: #E3F2FD;
  border-left: 4px solid #2196F3;
  padding: 15px;
  margin: 15px 0;
  border-radius: 0 8px 8px 0;
}

.try-this {
  background: #FFF3E0;
  border-left: 4px solid #FF9800;
  padding: 15px;
  margin: 15px 0;
  border-radius: 0 8px 8px 0;
}

.code-block {
  background: #263238;
  color: #aed581;
  padding: 15px;
  border-radius: 8px;
  overflow-x: auto;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 13px;
  line-height: 1.5;
}

.hidden-code {
  display: none;
}

.reveal-button {
  background: #009688;
  margin: 10px 0;
}

.graph-container {
  width: 100%;
  height: 300px;
  background: white;
  border: 2px solid #ddd;
  border-radius: 8px;
  position: relative;
  overflow: hidden;
}

.node {
  position: absolute;
  width: 80px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  font-weight: bold;
  font-size: 14px;
  transition: all 0.3s ease;
}

.node.updating {
  animation: node-flash 0.5s ease-in-out;
}

@keyframes node-flash {
  0%, 100% { transform: scale(1); box-shadow: none; }
  50% { transform: scale(1.1); box-shadow: 0 0 20px rgba(244, 67, 54, 0.5); }
}

.connection {
  position: absolute;
  background: #999;
  transform-origin: left center;
  height: 2px;
  transition: all 0.3s ease;
}

.connection.active {
  background: #f44336;
  height: 4px;
  box-shadow: 0 0 10px rgba(244, 67, 54, 0.5);
}

.state-indicator {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 8px;
}

.state-clean { background: #4CAF50; }
.state-dirty { background: #FF9800; }
.state-evaluating { background: #f44336; }
</style>

# Signals: An Interactive Playground

*An explorable explanation of reactive programming*

---

## 1. The Living Variable

Imagine a variable that **notifies** you when it changes. This is the essence of a **signal**.

<div class="interactive-container">
  <div class="control-panel">
    <h3>🔧 Interactive Signal</h3>
    <div class="slider-container">
      <label>temperature = <span id="temp-value" class="value-display">20</span>°C</label>
      <input type="range" id="temp-slider" min="0" max="100" value="20">
    </div>
    <div id="temp-log" style="margin-top: 10px; max-height: 150px; overflow-y: auto; background: #f5f5f5; padding: 10px; border-radius: 4px;"></div>
  </div>
</div>

<script>
(function() {
  const slider = document.getElementById('temp-slider');
  const display = document.getElementById('temp-value');
  const log = document.getElementById('temp-log');
  let changeCount = 0;
  
  function logChange(oldVal, newVal) {
    changeCount++;
    const entry = document.createElement('div');
    entry.className = 'log-entry';
    entry.innerHTML = `<strong>#${changeCount}</strong>: ${oldVal}°C → ${newVal}°C at ${new Date().toLocaleTimeString()}`;
    log.insertBefore(entry, log.firstChild);
    if (log.children.length > 10) log.removeChild(log.lastChild);
  }
  
  let lastValue = slider.value;
  slider.addEventListener('input', function() {
    const newValue = this.value;
    display.textContent = newValue;
    logChange(lastValue, newValue);
    lastValue = newValue;
  });
})();
</script>

<div class="explanation-box">
<strong>What's happening?</strong> As you drag the slider, the variable updates and automatically logs every change. In a normal program, you'd need to manually track changes. A <strong>signal</strong> does this automatically.
</div>

### The Signal Concept

A signal has two operations:
- **.get()** - Read the current value
- **.set(newValue)** - Change the value (notifies watchers)

<div class="try-this">
<strong>🎯 Try this:</strong> Drag the slider rapidly. Notice how every change is tracked with a timestamp. This is the foundation of reactivity: <em>observable state</em>.
</div>

---

## 2. The Dependency Graph

Signals become powerful when they **depend on each other**. This creates a living computation graph.

<div class="interactive-container">
  <div class="control-panel">
    <h3>🕸️ Living Dependency Graph</h3>
    <div class="graph-container" id="graph1" style="height: 250px;">
      <!-- Nodes -->
      <div class="node signal-node signal-source" id="node-a" style="left: 50px; top: 100px;">a = <span class="node-value">5</span></div>
      <div class="node signal-node signal-source" id="node-b" style="left: 50px; top: 180px;">b = <span class="node-value">3</span></div>
      <div class="node signal-node signal-computed" id="node-sum" style="left: 250px; top: 140px;">sum = <span class="node-value">8</span></div>
      
      <!-- Connections (drawn with CSS) -->
      <div class="connection" id="conn-a-sum" style="left: 130px; top: 122px; width: 120px; transform: rotate(-10deg);"></div>
      <div class="connection" id="conn-b-sum" style="left: 130px; top: 202px; width: 120px; transform: rotate(10deg);"></div>
    </div>
    
    <div style="margin-top: 15px;">
      <label>Signal a: <input type="number" id="input-a" value="5" style="width: 60px;"></label>
      <label style="margin-left: 20px;">Signal b: <input type="number" id="input-b" value="3" style="width: 60px;"></label>
      <button onclick="randomizeGraph1()" style="margin-left: 20px;">🎲 Randomize</button>
    </div>
    
    <div id="graph1-log" style="margin-top: 10px; font-size: 12px; color: #666;"></div>
  </div>
</div>

<script>
(function() {
  const inputA = document.getElementById('input-a');
  const inputB = document.getElementById('input-b');
  const nodeA = document.getElementById('node-a');
  const nodeB = document.getElementById('node-b');
  const nodeSum = document.getElementById('node-sum');
  const connASum = document.getElementById('conn-a-sum');
  const connBSum = document.getElementById('conn-b-sum');
  const log = document.getElementById('graph1-log');
  
  function updateGraph() {
    const a = parseInt(inputA.value) || 0;
    const b = parseInt(inputB.value) || 0;
    const sum = a + b;
    
    // Update visual nodes
    nodeA.querySelector('.node-value').textContent = a;
    nodeB.querySelector('.node-value').textContent = b;
    nodeSum.querySelector('.node-value').textContent = sum;
    
    // Animate propagation
    nodeA.classList.add('updating');
    connASum.classList.add('active');
    
    setTimeout(() => {
      nodeB.classList.add('updating');
      connBSum.classList.add('active');
    }, 100);
    
    setTimeout(() => {
      nodeSum.classList.add('updating');
      log.innerHTML = `<span style="color: #f44336;">⚡</span> sum updated: ${a} + ${b} = ${sum}`;
    }, 200);
    
    setTimeout(() => {
      nodeA.classList.remove('updating');
      nodeB.classList.remove('updating');
      nodeSum.classList.remove('updating');
      connASum.classList.remove('active');
      connBSum.classList.remove('active');
    }, 600);
  }
  
  window.randomizeGraph1 = function() {
    inputA.value = Math.floor(Math.random() * 20);
    inputB.value = Math.floor(Math.random() * 20);
    updateGraph();
  };
  
  inputA.addEventListener('input', updateGraph);
  inputB.addEventListener('input', updateGraph);
  
  // Initial update
  updateGraph();
})();
</script>

<div class="explanation-box">
<strong>The Graph Structure:</strong><br>
<span class="state-indicator state-clean"></span> <strong>Source nodes</strong> (green) = Mutable signals<br>
<span class="state-indicator state-clean" style="background: #2196F3;"></span> <strong>Computed nodes</strong> (blue) = Derived values<br>
<strong>Arrows</strong> = Dependencies (data flows downstream)
</div>

### How It Works

When `a` or `b` changes:
1. The change **propagates** along the arrows
2. `sum` is marked as "dirty" (needs recalculation)
3. When `sum.get()` is called, it **lazily** recalculates
4. The new value flows to any effects watching `sum`

<div class="try-this">
<strong>🎯 Try this:</strong> Change the values and watch the animation. The red flash shows propagation. Notice how both inputs can change sum, and sum always stays consistent.
</div>

---

## 3. The Diamond Problem

Here's where reactive systems prove their intelligence. Consider this graph:

<div class="interactive-container">
  <div class="control-panel">
    <h3>💎 The Diamond Challenge</h3>
    <div class="graph-container" id="diamond-graph" style="height: 300px;">
      <!-- Diamond layout -->
      <div class="node signal-node signal-source" id="diamond-base" style="left: 150px; top: 30px;">base = <span class="node-value">10</span></div>
      
      <div class="node signal-node signal-computed" id="diamond-left" style="left: 50px; top: 120px;">×2 = <span class="node-value">20</span></div>
      <div class="node signal-node signal-computed" id="diamond-right" style="left: 250px; top: 120px;">+5 = <span class="node-value">15</span></div>
      
      <div class="node signal-node signal-computed" id="diamond-total" style="left: 150px; top: 210px;">total = <span class="node-value">35</span></div>
      
      <!-- Connections -->
      <div class="connection" id="diamond-conn-base-left" style="left: 190px; top: 80px; width: 100px; transform: rotate(35deg);"></div>
      <div class="connection" id="diamond-conn-base-right" style="left: 230px; top: 80px; width: 100px; transform: rotate(-35deg);"></div>
      <div class="connection" id="diamond-conn-left-total" style="left: 130px; top: 168px; width: 100px; transform: rotate(35deg);"></div>
      <div class="connection" id="diamond-conn-right-total" style="left: 210px; top: 168px; width: 100px; transform: rotate(-35deg);"></div>
    </div>
    
    <div class="slider-container">
      <label>base value: <span id="diamond-base-display" class="value-display">10</span></label>
      <input type="range" id="diamond-slider" min="0" max="50" value="10">
    </div>
    
    <div style="display: flex; justify-content: space-between; margin-top: 15px; font-size: 12px;">
      <div>
        <strong>left evaluation count:</strong> <span id="left-count" class="value-display">1</span>
      </div>
      <div>
        <strong>right evaluation count:</strong> <span id="right-count" class="value-display">1</span>
      </div>
      <div>
        <strong>total evaluation count:</strong> <span id="total-count" class="value-display">1</span>
      </div>
    </div>
    
    <div class="explanation-box" style="margin-top: 15px;">
      <strong>The Challenge:</strong> When base changes, both left and right need updating. But if total reads both, will it recalculate twice? A naive system would glitch. A proper reactive system handles this elegantly.
    </div>
  </div>
</div>

<script>
(function() {
  const slider = document.getElementById('diamond-slider');
  const baseDisplay = document.getElementById('diamond-base-display');
  const baseNode = document.getElementById('diamond-base');
  const leftNode = document.getElementById('diamond-left');
  const rightNode = document.getElementById('diamond-right');
  const totalNode = document.getElementById('diamond-total');
  const leftCount = document.getElementById('left-count');
  const rightCount = document.getElementById('right-count');
  const totalCount = document.getElementById('total-count');
  
  const conns = [
    document.getElementById('diamond-conn-base-left'),
    document.getElementById('diamond-conn-base-right'),
    document.getElementById('diamond-conn-left-total'),
    document.getElementById('diamond-conn-right-total')
  ];
  
  let counts = { left: 1, right: 1, total: 1 };
  let lastValue = 10;
  
  function animatePropagation() {
    const base = parseInt(slider.value);
    if (base === lastValue) return;
    lastValue = base;
    
    // Update base
    baseDisplay.textContent = base;
    baseNode.querySelector('.node-value').textContent = base;
    baseNode.classList.add('updating');
    
    // Animate to left and right
    setTimeout(() => {
      conns[0].classList.add('active');
      conns[1].classList.add('active');
      
      setTimeout(() => {
        const left = base * 2;
        const right = base + 5;
        
        leftNode.querySelector('.node-value').textContent = left;
        rightNode.querySelector('.node-value').textContent = right;
        leftNode.classList.add('updating');
        rightNode.classList.add('updating');
        
        counts.left++;
        counts.right++;
        leftCount.textContent = counts.left;
        rightCount.textContent = counts.right;
        
        // Animate to total
        setTimeout(() => {
          conns[2].classList.add('active');
          conns[3].classList.add('active');
          
          setTimeout(() => {
            const total = left + right;
            totalNode.querySelector('.node-value').textContent = total;
            totalNode.classList.add('updating');
            
            counts.total++;
            totalCount.textContent = counts.total;
            
            // Cleanup
            setTimeout(() => {
              [baseNode, leftNode, rightNode, totalNode].forEach(n => n.classList.remove('updating'));
              conns.forEach(c => c.classList.remove('active'));
            }, 400);
          }, 150);
        }, 150);
      }, 150);
    }, 100);
  }
  
  slider.addEventListener('input', animatePropagation);
})();
</script>

### The Solution: Lazy Evaluation + Dirty Tracking

```javascript
// Simplified implementation showing the key insight
class Computed {
  get() {
    if (this.dirty) {
      this.recalculate();  // Only when needed!
    }
    return this.value;
  }
  
  markDirty() {
    this.dirty = true;
    // Notify downstream, but don't recalculate yet
    this.dependents.forEach(d => d.markDirty());
  }
}
```

The key insight: **mark dirty eagerly, recalculate lazily**. When `base` changes:
1. Both `left` and `right` are marked dirty immediately
2. When `total.get()` is called, it reads `left.get()` 
3. `left` recalculates (now clean), returns new value
4. `total` then reads `right.get()`
5. `right` recalculates (now clean), returns new value
6. `total` computes sum—**only one evaluation per node**

<div class="try-this">
<strong>🎯 Try this:</strong> Change the base value several times. Notice the evaluation counters—each computed value only runs once per change, even though total depends on two paths. This is <strong>glitch-free propagation</strong>.
</div>

---

## 4. Effects: When Values Meet the World

Signals and computeds are pure. But at some point, reactive values must affect the real world—update a display, log to console, send a network request. This is the job of **effects**.

<div class="interactive-container">
  <div class="control-panel">
    <h3>⚡ The Effect Boundary</h3>
    <div style="display: flex; align-items: center; gap: 20px; margin: 20px 0;">
      <div class="signal-node signal-computed" id="effect-source">doubled = 10</div>
      <div style="font-size: 24px;">→</div>
      <div class="signal-node signal-effect" id="effect-target" style="padding: 15px 25px;">
        <div>Effect</div>
        <div style="font-size: 12px; font-weight: normal; margin-top: 5px;">
          document.title = "10"
        </div>
      </div>
    </div>
    
    <div class="slider-container">
      <label>input: <span id="effect-input-display" class="value-display">5</span></label>
      <input type="range" id="effect-slider" min="0" max="100" value="5">
    </div>
    
    <div style="margin-top: 20px; padding: 15px; background: #263238; color: #aed581; border-radius: 8px; font-family: monospace; font-size: 13px;">
      <div style="color: #82b1ff; margin-bottom: 10px;">// Effect execution log:</div>
      <div id="effect-log" style="max-height: 150px; overflow-y: auto;"></div>
    </div>
    
    <div style="margin-top: 15px;">
      <button onclick="toggleEffect()" id="effect-toggle">⏸️ Stop Effect</button>
      <span style="margin-left: 15px; color: #666; font-size: 14px;">
        Effect status: <span id="effect-status" style="color: #4CAF50; font-weight: bold;">ACTIVE</span>
      </span>
    </div>
  </div>
</div>

<script>
(function() {
  const slider = document.getElementById('effect-slider');
  const inputDisplay = document.getElementById('effect-input-display');
  const sourceNode = document.getElementById('effect-source');
  const log = document.getElementById('effect-log');
  const statusSpan = document.getElementById('effect-status');
  const toggleBtn = document.getElementById('effect-toggle');
  
  let effectActive = true;
  let effectCount = 0;
  
  function addLogEntry(input, doubled) {
    effectCount++;
    const entry = document.createElement('div');
    entry.style.cssText = 'margin: 3px 0; padding: 3px 0; border-bottom: 1px solid #37474F;';
    entry.innerHTML = `<span style="color: #FF9800;">[${effectCount}]</span> input=${input} → doubled=${doubled} → effect ran at ${new Date().toLocaleTimeString()}`;
    log.insertBefore(entry, log.firstChild);
    if (log.children.length > 8) log.removeChild(log.lastChild);
  }
  
  function update() {
    const input = parseInt(slider.value);
    const doubled = input * 2;
    
    inputDisplay.textContent = input;
    sourceNode.textContent = `doubled = ${doubled}`;
    sourceNode.classList.add('updating');
    
    if (effectActive) {
      setTimeout(() => {
        document.getElementById('effect-target').classList.add('updating');
        addLogEntry(input, doubled);
        
        setTimeout(() => {
          document.getElementById('effect-target').classList.remove('updating');
        }, 300);
      }, 100);
    }
    
    setTimeout(() => {
      sourceNode.classList.remove('updating');
    }, 300);
  }
  
  window.toggleEffect = function() {
    effectActive = !effectActive;
    statusSpan.textContent = effectActive ? 'ACTIVE' : 'STOPPED';
    statusSpan.style.color = effectActive ? '#4CAF50' : '#f44336';
    toggleBtn.textContent = effectActive ? '⏸️ Stop Effect' : '▶️ Start Effect';
    
    if (effectActive) {
      // Re-run immediately when reactivating
      update();
    }
  };
  
  slider.addEventListener('input', update);
  update();
})();
</script>

### Effect Lifecycle

Effects follow a simple lifecycle:

1. **Create**: Start watching dependencies
2. **Run**: Execute when dependencies change (or initially)
3. **Stop**: Cleanup, remove from dependency graph

```javascript
const effect = watch(() => {
  console.log('Value changed to:', signal.get());
});

// Later: cleanup
effect.stop();
```

<div class="explanation-box">
<strong>Why effects matter:</strong> Effects are the <strong>output boundary</strong> of your reactive system. They bridge the pure reactive graph to the messy real world. Without effects, signals are just a calculation tree. With effects, they become a living system.
</div>

<div class="try-this">
<strong>🎯 Try this:</strong> Stop the effect, then change the slider. Notice no new log entries appear. Start it again—it immediately runs with the current value. This shows effect subscription is dynamic.
</div>

---

## 5. Batching: Atomic Updates

What happens when you change multiple signals at once? Without batching, you'd get intermediate, inconsistent states.

<div class="interactive-container">
  <div class="control-panel">
    <h3>📦 Batching in Action</h3>
    
    <div style="display: flex; gap: 20px; margin: 20px 0;">
      <div style="flex: 1; text-align: center;">
        <div class="signal-node signal-source">width = <span id="batch-width">10</span></div>
      </div>
      <div style="flex: 1; text-align: center;">
        <div class="signal-node signal-source">height = <span id="batch-height">10</span></div>
      </div>
      <div style="flex: 1; text-align: center;">
        <div class="signal-node signal-computed">area = <span id="batch-area">100</span></div>
      </div>
    </div>
    
    <div id="batch-visual" style="width: 100px; height: 100px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin: 20px auto; transition: all 0.3s ease; border: 3px solid #333; border-radius: 8px;">
    </div>
    
    <div style="margin: 20px 0;">
      <h4>Without Batching (Sequential Updates):</h4>
      <button onclick="updateSequential()">Update width then height</button>
      <div id="sequential-log" style="margin-top: 10px; font-size: 12px; color: #666;"></div>
    </div>
    
    <div style="margin: 20px 0;">
      <h4>With Batching (Atomic Update):</h4>
      <button onclick="updateBatched()">Batch update both</button>
      <div id="batched-log" style="margin-top: 10px; font-size: 12px; color: #666;"></div>
    </div>
  </div>
</div>

<script>
(function() {
  let width = 10;
  let height = 10;
  let batchDepth = 0;
  let pendingEffects = [];
  
  const widthDisplay = document.getElementById('batch-width');
  const heightDisplay = document.getElementById('batch-height');
  const areaDisplay = document.getElementById('batch-area');
  const visual = document.getElementById('batch-visual');
  const seqLog = document.getElementById('sequential-log');
  const batchLog = document.getElementById('batched-log');
  
  function updateVisual() {
    widthDisplay.textContent = width;
    heightDisplay.textContent = height;
    areaDisplay.textContent = width * height;
    visual.style.width = (width * 5) + 'px';
    visual.style.height = (height * 5) + 'px';
  }
  
  function triggerEffect(label, logEl) {
    const entry = document.createElement('div');
    entry.innerHTML = `<span style="color: #f44336;">⚡</span> Effect ran: ${label} → area = ${width * height} (w=${width}, h=${height})`;
    logEl.insertBefore(entry, logEl.firstChild);
    if (logEl.children.length > 5) logEl.removeChild(logEl.lastChild);
  }
  
  window.updateSequential = function() {
    width = Math.floor(Math.random() * 30) + 5;
    triggerEffect('width changed', seqLog);
    updateVisual();
    
    setTimeout(() => {
      height = Math.floor(Math.random() * 30) + 5;
      triggerEffect('height changed', seqLog);
      updateVisual();
    }, 300);
  };
  
  window.updateBatched = function() {
    const newWidth = Math.floor(Math.random() * 30) + 5;
    const newHeight = Math.floor(Math.random() * 30) + 5;
    
    const entry = document.createElement('div');
    entry.innerHTML = `<span style="color: #4CAF50;">📦</span> Batch started...`;
    batchLog.insertBefore(entry, batchLog.firstChild);
    
    // Simulate batch
    batchDepth++;
    width = newWidth;  // No effect yet
    height = newHeight; // No effect yet
    batchDepth--;
    
    // Flush at end
    setTimeout(() => {
      triggerEffect('batch complete', batchLog);
      updateVisual();
    }, 300);
  };
})();
</script>

### The Problem

Without batching:
```javascript
width.set(20);  // Effect sees: width=20, height=10, area=200
height.set(30); // Effect sees: width=20, height=30, area=600
```

The effect runs **twice**, and sees an intermediate state (200) that was never intended to exist.

### The Solution

With batching:
```javascript
batch(() => {
  width.set(20);  // Deferred
  height.set(30); // Deferred
}); // Effects run once with final state

// Effect sees: width=20, height=30, area=600 (once)
```

<div class="explanation-box">
<strong>Glitch-Free Guarantee:</strong> Batching ensures that effects only see <strong>consistent states</strong>. The intermediate state (width updated, height not yet) never reaches observers. This is crucial for UI consistency—you don't want to show a rectangle with width=20 and height=10 when the intention was 20×30.
</div>

<div class="try-this">
<strong>🎯 Try this:</strong> Run the sequential update. Notice the rectangle flashes through an intermediate size. Then run batched—the rectangle smoothly transitions to the final size. That's glitch-free propagation in action.
</div>

---

## 6. Inside the Implementation

Now let's peek inside. Here's a minimal but complete signal implementation:

<button class="reveal-button" onclick="document.getElementById('impl-code').classList.toggle('hidden-code')">🔍 Reveal Implementation</button>

<div id="impl-code" class="hidden-code">
<div class="code-block">
<pre>// Minimal Signal Implementation (simplified from loupedeck)

class Runtime {
  currentCollector = null;  // Who's reading right now
  batchDepth = 0;           // Batch nesting level
  pendingEffects = new Set(); // Effects to run
  
  trackDependency(source) {
    if (this.currentCollector) {
      this.currentCollector.trackDependency(source);
    }
  }
  
  batch(fn) {
    this.batchDepth++;
    fn();
    this.batchDepth--;
    if (this.batchDepth === 0) this.flush();
  }
  
  flush() {
    while (this.pendingEffects.size > 0) {
      const effects = [...this.pendingEffects];
      this.pendingEffects.clear();
      effects.forEach(e => e.run());
    }
  }
}

class Signal {
  constructor(runtime, value) {
    this.rt = runtime;
    this.value = value;
    this.dependents = new Set();
  }
  
  get() {
    this.rt.trackDependency(this);
    return this.value;
  }
  
  set(newValue) {
    if (this.value === newValue) return; // Equality check!
    this.value = newValue;
    
    // Mark all dependents dirty
    this.dependents.forEach(dep => dep.markDirty());
    
    // Schedule flush if not batching
    if (this.rt.batchDepth === 0) this.rt.flush();
  }
  
  addDependent(dep) { this.dependents.add(dep); }
  removeDependent(dep) { this.dependents.delete(dep); }
}

class Computed {
  constructor(runtime, computeFn) {
    this.rt = runtime;
    this.fn = computeFn;
    this.value = undefined;
    this.dirty = true;
    this.dependencies = [];
    this.dependents = new Set();
    this.evaluating = false;
  }
  
  get() {
    this.rt.trackDependency(this);
    
    if (this.dirty) {
      if (this.evaluating) throw new Error("Cycle detected!");
      this.evaluate();
    }
    return this.value;
  }
  
  evaluate() {
    this.evaluating = true;
    
    // Cleanup old dependencies
    this.dependencies.forEach(dep => dep.removeDependent(this));
    this.dependencies = [];
    
    // Collect new dependencies
    const prevCollector = this.rt.currentCollector;
    this.rt.currentCollector = this;
    this.value = this.fn();
    this.rt.currentCollector = prevCollector;
    
    this.dirty = false;
    this.evaluating = false;
  }
  
  markDirty() {
    if (this.dirty) return;
    this.dirty = true;
    // Propagate downstream
    this.dependents.forEach(dep => dep.markDirty());
  }
  
  trackDependency(source) {
    this.dependencies.push(source);
    source.addDependent(this);
  }
  
  addDependent(dep) { this.dependents.add(dep); }
  removeDependent(dep) { this.dependents.delete(dep); }
}

class Effect {
  constructor(runtime, fn) {
    this.rt = runtime;
    this.fn = fn;
    this.active = true;
    this.dirty = true;
    this.dependencies = [];
    this.evaluating = false;
  }
  
  run() {
    if (!this.active) return;
    if (this.evaluating) throw new Error("Reentrant effect!");
    this.evaluating = true;
    
    // Cleanup and rebuild dependencies
    this.dependencies.forEach(dep => dep.removeDependent(this));
    this.dependencies = [];
    
    const prevCollector = this.rt.currentCollector;
    this.rt.currentCollector = this;
    this.fn();
    this.rt.currentCollector = prevCollector;
    
    this.dirty = false;
    this.evaluating = false;
  }
  
  markDirty() {
    if (!this.active || this.dirty) return;
    this.dirty = true;
    this.rt.pendingEffects.add(this);
  }
  
  trackDependency(source) {
    this.dependencies.push(source);
    source.addDependent(this);
  }
  
  stop() {
    this.active = false;
    this.dependencies.forEach(dep => dep.removeDependent(this));
    this.rt.pendingEffects.delete(this);
  }
}</pre>
</div>
</div>

### Key Algorithms Explained

#### 1. Dependency Collection ("Who reads me?")

When a computed or effect runs:
```javascript
// Set global context
runtime.currentCollector = this;

// Execute function - any .get() calls will register
trackDependency(source) {
  if (runtime.currentCollector) {
    // Source: "add this computed/effect as my dependent"
    source.addDependent(runtime.currentCollector);
    // Computed/effect: "track this as my dependency"
    runtime.currentCollector.dependencies.push(source);
  }
}
```

This is **implicit** dependency tracking—you don't declare dependencies, they're discovered automatically during execution.

#### 2. Propagation ("Who should update?")

When a signal changes:
```javascript
set(newValue) {
  this.value = newValue;
  // Eager: mark all downstream as dirty immediately
  this.dependents.forEach(dep => dep.markDirty());
}
```

Note: We mark dirty **eagerly** but recalculate **lazily**.

#### 3. Cycle Detection

```javascript
evaluate() {
  if (this.evaluating) throw new Error("Cycle!");
  this.evaluating = true;
  // ... do work ...
  this.evaluating = false;
}
```

If a computed tries to read itself (directly or indirectly) during evaluation, it catches itself.

---

## 7. Playground: Build Your Own

Now it's your turn. Use this live editor to experiment:

<div class="interactive-container">
  <div class="control-panel">
    <h3>🎮 Signal Playground</h3>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
      <div>
        <div style="font-weight: bold; margin-bottom: 10px;">JavaScript Code:</div>
        <textarea id="playground-code" style="width: 100%; height: 200px; font-family: monospace; font-size: 13px; padding: 10px; border-radius: 4px; border: 2px solid #ddd;">// Create signals
const a = signal(5);
const b = signal(10);

// Create computed
const sum = computed(() => a.get() + b.get());

// Create effect
watch(() => {
  console.log('Sum is now:', sum.get());
});

// Change values
a.set(20);
b.set(30);</textarea>
        <button onclick="runPlayground()" style="margin-top: 10px; width: 100%;">▶️ Run Code</button>
      </div>
      <div>
        <div style="font-weight: bold; margin-bottom: 10px;">Output:</div>
        <div id="playground-output" style="width: 100%; height: 200px; background: #263238; color: #aed581; font-family: monospace; font-size: 13px; padding: 10px; border-radius: 4px; overflow-y: auto;">
          // Output will appear here...
        </div>
        <button onclick="clearOutput()" style="margin-top: 10px; width: 100%;">🗑️ Clear</button>
      </div>
    </div>
    
    <div style="margin-top: 15px; display: flex; gap: 10px; flex-wrap: wrap;">
      <button onclick="loadExample('basic')">📋 Basic</button>
      <button onclick="loadExample('chained')">⛓️ Chained</button>
      <button onclick="loadExample('diamond')">💎 Diamond</button>
      <button onclick="loadExample('conditional')">🔀 Conditional</button>
    </div>
  </div>
</div>

<script>
(function() {
  const output = document.getElementById('playground-output');
  const codeArea = document.getElementById('playground-code');
  
  const examples = {
    basic: `// Create signals
const a = signal(5);
const b = signal(10);

// Create computed
const sum = computed(() => a.get() + b.get());

// Create effect
watch(() => {
  console.log('Sum is now:', sum.get());
});

// Change values
a.set(20);
b.set(30);`,
    
    chained: `// Chain of computeds
const base = signal(2);

const doubled = computed(() => base.get() * 2);
const quadrupled = computed(() => doubled.get() * 2);

watch(() => {
  console.log('base:', base.get(), '→ doubled:', doubled.get(), '→ quadrupled:', quadrupled.get());
});

base.set(5);
base.set(10);`,
    
    diamond: `// Diamond dependency pattern
const base = signal(10);

const left = computed(() => base.get() + 1);
const right = computed(() => base.get() * 2);
const total = computed(() => left.get() + right.get());

let runs = 0;
watch(() => {
  runs++;
  console.log('Run #' + runs + ': total =', total.get());
});

// Only one effect run per change
base.set(20);
base.set(30);`,
    
    conditional: `// Dynamic dependencies
const useBonus = signal(true);
const base = signal(100);
const bonus = signal(50);

// Dependencies change based on condition!
const total = computed(() => {
  if (useBonus.get()) {
    return base.get() + bonus.get();
  }
  return base.get();
});

watch(() => {
  console.log('Total:', total.get(), '(useBonus:', useBonus.get() + ')');
});

// These trigger updates
useBonus.set(false);
base.set(200);

// This does NOT trigger (bonus not a dependency when useBonus=false)
bonus.set(999);
useBonus.set(true); // Now bonus is 999!`
  };
  
  window.loadExample = function(name) {
    codeArea.value = examples[name];
  };
  
  window.clearOutput = function() {
    output.innerHTML = '// Output will appear here...';
  };
  
  window.runPlayground = function() {
    output.innerHTML = '';
    
    // Minimal reactive system implementation
    const logs = [];
    
    function log(msg) {
      logs.push(msg);
      output.innerHTML = logs.join('\n');
      output.scrollTop = output.scrollHeight;
    }
    
    class Runtime {
      constructor() {
        this.currentCollector = null;
        this.batchDepth = 0;
        this.pendingEffects = new Set();
      }
      
      trackDependency(source) {
        if (this.currentCollector) {
          source.addDependent(this.currentCollector);
          this.currentCollector.dependencies.push(source);
        }
      }
      
      batch(fn) {
        this.batchDepth++;
        fn();
        this.batchDepth--;
        if (this.batchDepth === 0) this.flush();
      }
      
      flush() {
        while (this.pendingEffects.size > 0) {
          const effects = [...this.pendingEffects];
          this.pendingEffects.clear();
          effects.forEach(e => {
            if (e.active && e.dirty) e.run();
          });
        }
      }
    }
    
    class Signal {
      constructor(runtime, value) {
        this.rt = runtime;
        this.value = value;
        this.dependents = new Set();
      }
      
      get() {
        this.rt.trackDependency(this);
        return this.value;
      }
      
      set(newValue) {
        if (this.value === newValue) return;
        this.value = newValue;
        this.dependents.forEach(dep => dep.markDirty());
        if (this.rt.batchDepth === 0) this.rt.flush();
      }
      
      addDependent(dep) { this.dependents.add(dep); }
      removeDependent(dep) { this.dependents.delete(dep); }
    }
    
    class Computed {
      constructor(runtime, fn) {
        this.rt = runtime;
        this.fn = fn;
        this.value = undefined;
        this.dirty = true;
        this.dependencies = [];
        this.dependents = new Set();
        this.evaluating = false;
      }
      
      get() {
        this.rt.trackDependency(this);
        if (this.dirty) {
          if (this.evaluating) {
            log('ERROR: Cycle detected!');
            return undefined;
          }
          this.evaluate();
        }
        return this.value;
      }
      
      evaluate() {
        this.evaluating = true;
        this.dependencies.forEach(dep => dep.removeDependent(this));
        this.dependencies = [];
        
        const prev = this.rt.currentCollector;
        this.rt.currentCollector = this;
        this.value = this.fn();
        this.rt.currentCollector = prev;
        
        this.dirty = false;
        this.evaluating = false;
      }
      
      markDirty() {
        if (this.dirty) return;
        this.dirty = true;
        this.dependents.forEach(dep => dep.markDirty());
      }
      
      addDependent(dep) { this.dependents.add(dep); }
      removeDependent(dep) { this.dependents.delete(dep); }
    }
    
    class Effect {
      constructor(runtime, fn) {
        this.rt = runtime;
        this.fn = fn;
        this.active = true;
        this.dirty = true;
        this.dependencies = [];
        this.evaluating = false;
      }
      
      run() {
        if (!this.active) return;
        if (this.evaluating) {
          log('ERROR: Reentrant effect!');
          return;
        }
        this.evaluating = true;
        
        this.dependencies.forEach(dep => dep.removeDependent(this));
        this.dependencies = [];
        
        const prev = this.rt.currentCollector;
        this.rt.currentCollector = this;
        this.fn();
        this.rt.currentCollector = prev;
        
        this.dirty = false;
        this.evaluating = false;
      }
      
      markDirty() {
        if (!this.active || this.dirty) return;
        this.dirty = true;
        this.rt.pendingEffects.add(this);
      }
    }
    
    const rt = new Runtime();
    
    function signal(value) {
      return new Signal(rt, value);
    }
    
    function computed(fn) {
      const c = new Computed(rt, fn);
      return {
        get: () => c.get()
      };
    }
    
    function watch(fn) {
      const e = new Effect(rt, () => {
        fn();
      });
      e.run();
    }
    
    // Capture console.log
    const originalLog = console.log;
    console.log = (...args) => {
      log(args.join(' '));
    };
    
    try {
      eval(codeArea.value);
    } catch (err) {
      log('ERROR: ' + err.message);
    }
    
    console.log = originalLog;
  };
})();
</script>

<div class="try-this">
<strong>🎯 Experiments to try:</strong>
<ul>
<li><strong>Chained:</strong> Notice how changes propagate through multiple levels of computed values</li>
<li><strong>Diamond:</strong> Verify that total only triggers one effect per change (not two!)</li>
<li><strong>Conditional:</strong> See how dependencies are dynamic—bonus doesn't trigger when useBonus is false</li>
<li><strong>Create your own:</strong> Try making a signal that depends on itself (cycle detection!)</li>
</ul>
</div>

---

## 8. The Connection to History

Remember SICP Section 3.5? Streams as signals? Here's the direct lineage:

<div class="interactive-container">
  <div style="display: flex; align-items: center; justify-content: space-around; flex-wrap: wrap; gap: 20px; padding: 20px;">
    <div style="text-align: center; padding: 20px; background: #E8F5E9; border-radius: 8px; flex: 1; min-width: 200px;">
      <div style="font-size: 48px;">📚</div>
      <h4>SICP (1984)</h4>
      <p style="font-size: 13px;">Section 3.5: Streams as signals<br>Section 3.3.5: Constraint propagation</p>
    </div>
    <div style="font-size: 36px; color: #666;">→</div>
    <div style="text-align: center; padding: 20px; background: #E3F2FD; border-radius: 8px; flex: 1; min-width: 200px;">
      <div style="font-size: 48px;">🎬</div>
      <h4>Fran (1997)</h4>
      <p style="font-size: 13px;">Functional Reactive Animation<br>Behaviors: Time → Value</p>
    </div>
    <div style="font-size: 36px; color: #666;">→</div>
    <div style="text-align: center; padding: 20px; background: #FFF3E0; border-radius: 8px; flex: 1; min-width: 200px;">
      <div style="font-size: 48px;">🌳</div>
      <h4>KnockoutJS (2010)</h4>
      <p style="font-size: 13px;">Implicit dependency tracking<br>Automatic UI updates</p>
    </div>
    <div style="font-size: 36px; color: #666;">→</div>
    <div style="text-align: center; padding: 20px; background: #F3E5F5; border-radius: 8px; flex: 1; min-width: 200px;">
      <div style="font-size: 48px;">⚡</div>
      <h4>SolidJS/Vue/Angular (2020+)</h4>
      <p style="font-size: 13px;">Fine-grained reactivity<br>Signals as primitives</p>
    </div>
  </div>
</div>

### The Unbroken Chain

What Sussman and Abelson called "streams," we now call "signals." What they called "constraint propagation," we call "dependency graphs." The vocabulary changed, but the ideas are the same:

| SICP Concept | Modern Equivalent |
|--------------|-------------------|
| `cons-stream` | Signal constructor |
| `stream-map` | `computed()` with transform |
| `force` (evaluate) | `.get()` on computed |
| Constraint network | Dependency graph |
| Propagation | Dirty marking + lazy eval |

The loupedeck implementation you analyzed earlier is a direct descendant—clean, minimal, and true to the original vision.

---

## Conclusion: The Living System

Signals transform static code into **living systems**. Instead of:

```javascript
// Imperative: You must remember to update everything
function updateUI() {
  const sum = a + b;
  document.getElementById('sum').textContent = sum;
  document.getElementById('total').textContent = sum + c;
  // What if you forget one?
}
```

You write:

```javascript
// Reactive: System maintains consistency
const sum = computed(() => a.get() + b.get());
const total = computed(() => sum.get() + c.get());
watch(() => {
  document.getElementById('sum').textContent = sum.get();
  document.getElementById('total').textContent = total.get();
});
// System guarantees consistency
```

This is the power of reactive programming: **declare relationships, let the system maintain them.**

---

## Further Exploration

<div class="explanation-box">
<strong>Where to go from here:</strong>
<ul>
<li><strong>Read the source:</strong> The loupedeck <code>runtime/reactive/</code> implementation is only ~400 lines of Go</li>
<li><strong>Try SolidJS:</strong> <a href="https://www.solidjs.com/">solidjs.com</a> - The purest modern signal implementation</li>
<li><strong>Study SICP:</strong> Section 3.5 on streams - Read the original vision</li>
<li><strong>Explore Preact Signals:</strong> Framework-agnostic signals you can use anywhere</li>
<li><strong>Watch "A Hands-on Introduction to Fine-Grained Reactivity"</strong> by Ryan Carniato</li>
</ul>
</div>

---

<div style="text-align: center; padding: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 8px; margin-top: 40px;">
  <h2 style="margin: 0;">The End</h2>
  <p style="margin: 10px 0 0 0; font-size: 16px;">But your exploration of reactive systems is just beginning.</p>
  <p style="margin: 20px 0 0 0; font-size: 14px; opacity: 0.9;">
    "Programs must be written for people to read, and only incidentally for machines to execute."<br>
    — SICP
  </p>
</div>

---

*This interactive article was created as part of TECH-REPORT-2026-04-12. Run the Go experiments in `reactive-experiments.go` to see these concepts in action.*
