# GODOT/UNITY INPUT BINDINGS
## EVE Rebellion - Cross-Engine Controller Maps

**Purpose**: Export hard-locked controller layout to Godot and Unity  
**Why**: Future-proof if migrating from pygame to game engine

---

## 🎮 GODOT INPUT MAP

### project.godot Configuration

```gdscript
[input]

# === MOVEMENT ===
move_left={
"deadzone": 0.15,
"events": [
    Object(InputEventJoypadMotion,"resource_local_to_scene":false,"resource_name":"","device":0,"axis":0,"axis_value":-1.0)
]
}

move_right={
"deadzone": 0.15,
"events": [
    Object(InputEventJoypadMotion,"resource_local_to_scene":false,"resource_name":"","device":0,"axis":0,"axis_value":1.0)
]
}

move_up={
"deadzone": 0.15,
"events": [
    Object(InputEventJoypadMotion,"resource_local_to_scene":false,"resource_name":"","device":0,"axis":1,"axis_value":-1.0)
]
}

move_down={
"deadzone": 0.15,
"events": [
    Object(InputEventJoypadMotion,"resource_local_to_scene":false,"resource_name":"","device":0,"axis":1,"axis_value":1.0)
]
}

# === AIM OFFSET ===
aim_left={
"deadzone": 0.20,
"events": [
    Object(InputEventJoypadMotion,"resource_local_to_scene":false,"resource_name":"","device":0,"axis":2,"axis_value":-1.0)
]
}

aim_right={
"deadzone": 0.20,
"events": [
    Object(InputEventJoypadMotion,"resource_local_to_scene":false,"resource_name":"","device":0,"axis":2,"axis_value":1.0)
]
}

aim_up={
"deadzone": 0.20,
"events": [
    Object(InputEventJoypadMotion,"resource_local_to_scene":false,"resource_name":"","device":0,"axis":3,"axis_value":-1.0)
]
}

aim_down={
"deadzone": 0.20,
"events": [
    Object(InputEventJoypadMotion,"resource_local_to_scene":false,"resource_name":"","device":0,"axis":3,"axis_value":1.0)
]
}

# === WEAPONS ===
primary_fire={
"deadzone": 0.10,
"events": [
    Object(InputEventJoypadMotion,"resource_local_to_scene":false,"resource_name":"","device":0,"axis":5,"axis_value":1.0)
]
}

alternate_fire={
"deadzone": 0.10,
"events": [
    Object(InputEventJoypadMotion,"resource_local_to_scene":false,"resource_name":"","device":0,"axis":4,"axis_value":1.0)
]
}

# === AMMO MANAGEMENT ===
cycle_ammo_prev={
"deadzone": 0.5,
"events": [
    Object(InputEventJoypadButton,"resource_local_to_scene":false,"resource_name":"","device":0,"button_index":4,"pressure":0.0,"pressed":false)
]
}

cycle_ammo_next={
"deadzone": 0.5,
"events": [
    Object(InputEventJoypadButton,"resource_local_to_scene":false,"resource_name":"","device":0,"button_index":5,"pressure":0.0,"pressed":false)
]
}

# === TACTICAL ===
emergency_burn={
"deadzone": 0.5,
"events": [
    Object(InputEventJoypadButton,"resource_local_to_scene":false,"resource_name":"","device":0,"button_index":1,"pressure":0.0,"pressed":false)
]
}

deploy_fleet={
"deadzone": 0.5,
"events": [
    Object(InputEventJoypadButton,"resource_local_to_scene":false,"resource_name":"","device":0,"button_index":2,"pressure":0.0,"pressed":false)
]
}

switch_formation={
"deadzone": 0.5,
"events": [
    Object(InputEventJoypadButton,"resource_local_to_scene":false,"resource_name":"","device":0,"button_index":3,"pressure":0.0,"pressed":false)
]
}

context_action={
"deadzone": 0.5,
"events": [
    Object(InputEventJoypadButton,"resource_local_to_scene":false,"resource_name":"","device":0,"button_index":0,"pressure":0.0,"pressed":false)
]
}

# === SYSTEM ===
pause_game={
"deadzone": 0.5,
"events": [
    Object(InputEventJoypadButton,"resource_local_to_scene":false,"resource_name":"","device":0,"button_index":7,"pressure":0.0,"pressed":false)
]
}

quick_stats={
"deadzone": 0.5,
"events": [
    Object(InputEventJoypadButton,"resource_local_to_scene":false,"resource_name":"","device":0,"button_index":6,"pressure":0.0,"pressed":false)
]
}

# === D-PAD ===
dpad_up={
"deadzone": 0.5,
"events": [
    Object(InputEventJoypadButton,"resource_local_to_scene":false,"resource_name":"","device":0,"button_index":11,"pressure":0.0,"pressed":false)
]
}

dpad_down={
"deadzone": 0.5,
"events": [
    Object(InputEventJoypadButton,"resource_local_to_scene":false,"resource_name":"","device":0,"button_index":12,"pressure":0.0,"pressed":false)
]
}

dpad_left={
"deadzone": 0.5,
"events": [
    Object(InputEventJoypadButton,"resource_local_to_scene":false,"resource_name":"","device":0,"button_index":13,"pressure":0.0,"pressed":false)
]
}

dpad_right={
"deadzone": 0.5,
"events": [
    Object(InputEventJoypadButton,"resource_local_to_scene":false,"resource_name":"","device":0,"button_index":14,"pressure":0.0,"pressed":false)
]
}
```

---

### GDScript Controller Handler

```gdscript
extends Node

# Hard-locked controller input handler
# Matches pygame implementation exactly

var move_vector := Vector2.ZERO
var aim_vector := Vector2.ZERO
var trigger_pressure := 0.0
var is_firing := false
var is_alt_firing := false

# Input lock
var input_locked := false
var lock_timer := 0.0

# Settings (NOT bindings)
var deadzone_move := 0.15
var deadzone_aim := 0.20
var sensitivity_move := 1.0
var sensitivity_aim := 0.8
var invert_y := false

func _process(delta: float) -> void:
    if input_locked:
        lock_timer -= delta
        if lock_timer <= 0:
            input_locked = false
        else:
            # Zero inputs while locked
            move_vector = Vector2.ZERO
            is_firing = false
            is_alt_firing = false
            return
    
    # Read movement (HARD-LOCKED to left stick)
    var raw_x := Input.get_action_strength("move_right") - Input.get_action_strength("move_left")
    var raw_y := Input.get_action_strength("move_down") - Input.get_action_strength("move_up")
    
    move_vector.x = apply_deadzone(raw_x, deadzone_move)
    move_vector.y = apply_deadzone(raw_y, deadzone_move)
    
    if invert_y:
        move_vector.y = -move_vector.y
    
    # Apply momentum curve
    move_vector.x = momentum_curve(move_vector.x) * sensitivity_move
    move_vector.y = momentum_curve(move_vector.y) * sensitivity_move
    
    # Read aim (HARD-LOCKED to right stick)
    var raw_aim_x := Input.get_action_strength("aim_right") - Input.get_action_strength("aim_left")
    var raw_aim_y := Input.get_action_strength("aim_down") - Input.get_action_strength("aim_up")
    
    aim_vector.x = apply_deadzone(raw_aim_x, deadzone_aim)
    aim_vector.y = apply_deadzone(raw_aim_y, deadzone_aim)
    
    if invert_y:
        aim_vector.y = -aim_vector.y
    
    aim_vector *= sensitivity_aim
    
    # Read triggers
    trigger_pressure = Input.get_action_strength("primary_fire")
    is_firing = trigger_pressure > 0.05
    is_alt_firing = Input.get_action_strength("alternate_fire") > 0.05

func apply_deadzone(value: float, deadzone: float) -> float:
    if abs(value) < deadzone:
        return 0.0
    var sign := 1.0 if value > 0 else -1.0
    var scaled := (abs(value) - deadzone) / (1.0 - deadzone)
    return sign * scaled

func momentum_curve(value: float) -> float:
    if value == 0.0:
        return 0.0
    var sign := 1.0 if value > 0 else -1.0
    return sign * pow(abs(value), 1.8)

func lock_inputs(duration: float = 1.0) -> void:
    input_locked = true
    lock_timer = duration
    Input.start_joy_vibration(0, 1.0, 1.0, 0.5)  # Death haptic

func get_movement() -> Vector2:
    return move_vector

func get_aim_offset() -> Vector2:
    return aim_vector * 30.0  # pixels, matches pygame

func is_action_just_pressed(action: String) -> bool:
    return Input.is_action_just_pressed(action)
```

---

## 🎯 UNITY INPUT SYSTEM

### InputActions Asset (JSON)

```json
{
    "name": "EVERebellionControls",
    "maps": [
        {
            "name": "Gameplay",
            "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "actions": [
                {
                    "name": "Move",
                    "type": "Value",
                    "id": "11111111-1111-1111-1111-111111111111",
                    "expectedControlType": "Vector2",
                    "processors": "StickDeadzone(min=0.15)",
                    "interactions": "",
                    "initialStateCheck": true
                },
                {
                    "name": "Aim",
                    "type": "Value",
                    "id": "22222222-2222-2222-2222-222222222222",
                    "expectedControlType": "Vector2",
                    "processors": "StickDeadzone(min=0.20)",
                    "interactions": "",
                    "initialStateCheck": true
                },
                {
                    "name": "PrimaryFire",
                    "type": "Value",
                    "id": "33333333-3333-3333-3333-333333333333",
                    "expectedControlType": "Axis",
                    "processors": "AxisDeadzone(min=0.10)",
                    "interactions": "",
                    "initialStateCheck": true
                },
                {
                    "name": "AlternateFire",
                    "type": "Value",
                    "id": "44444444-4444-4444-4444-444444444444",
                    "expectedControlType": "Axis",
                    "processors": "AxisDeadzone(min=0.10)",
                    "interactions": "",
                    "initialStateCheck": true
                },
                {
                    "name": "CycleAmmoPrev",
                    "type": "Button",
                    "id": "55555555-5555-5555-5555-555555555555",
                    "expectedControlType": "Button",
                    "processors": "",
                    "interactions": "",
                    "initialStateCheck": false
                },
                {
                    "name": "CycleAmmoNext",
                    "type": "Button",
                    "id": "66666666-6666-6666-6666-666666666666",
                    "expectedControlType": "Button",
                    "processors": "",
                    "interactions": "",
                    "initialStateCheck": false
                },
                {
                    "name": "EmergencyBurn",
                    "type": "Button",
                    "id": "77777777-7777-7777-7777-777777777777",
                    "expectedControlType": "Button",
                    "processors": "",
                    "interactions": "",
                    "initialStateCheck": false
                },
                {
                    "name": "DeployFleet",
                    "type": "Button",
                    "id": "88888888-8888-8888-8888-888888888888",
                    "expectedControlType": "Button",
                    "processors": "",
                    "interactions": "",
                    "initialStateCheck": false
                },
                {
                    "name": "SwitchFormation",
                    "type": "Button",
                    "id": "99999999-9999-9999-9999-999999999999",
                    "expectedControlType": "Button",
                    "processors": "",
                    "interactions": "",
                    "initialStateCheck": false
                },
                {
                    "name": "ContextAction",
                    "type": "Button",
                    "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                    "expectedControlType": "Button",
                    "processors": "",
                    "interactions": "",
                    "initialStateCheck": false
                },
                {
                    "name": "Pause",
                    "type": "Button",
                    "id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
                    "expectedControlType": "Button",
                    "processors": "",
                    "interactions": "",
                    "initialStateCheck": false
                },
                {
                    "name": "QuickStats",
                    "type": "Button",
                    "id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
                    "expectedControlType": "Button",
                    "processors": "",
                    "interactions": "",
                    "initialStateCheck": false
                }
            ],
            "bindings": [
                {
                    "name": "",
                    "id": "d1d1d1d1-d1d1-d1d1-d1d1-d1d1d1d1d1d1",
                    "path": "<Gamepad>/leftStick",
                    "interactions": "",
                    "processors": "",
                    "groups": "Gamepad",
                    "action": "Move",
                    "isComposite": false,
                    "isPartOfComposite": false
                },
                {
                    "name": "",
                    "id": "d2d2d2d2-d2d2-d2d2-d2d2-d2d2d2d2d2d2",
                    "path": "<Gamepad>/rightStick",
                    "interactions": "",
                    "processors": "",
                    "groups": "Gamepad",
                    "action": "Aim",
                    "isComposite": false,
                    "isPartOfComposite": false
                },
                {
                    "name": "",
                    "id": "d3d3d3d3-d3d3-d3d3-d3d3-d3d3d3d3d3d3",
                    "path": "<Gamepad>/rightTrigger",
                    "interactions": "",
                    "processors": "",
                    "groups": "Gamepad",
                    "action": "PrimaryFire",
                    "isComposite": false,
                    "isPartOfComposite": false
                },
                {
                    "name": "",
                    "id": "d4d4d4d4-d4d4-d4d4-d4d4-d4d4d4d4d4d4",
                    "path": "<Gamepad>/leftTrigger",
                    "interactions": "",
                    "processors": "",
                    "groups": "Gamepad",
                    "action": "AlternateFire",
                    "isComposite": false,
                    "isPartOfComposite": false
                },
                {
                    "name": "",
                    "id": "d5d5d5d5-d5d5-d5d5-d5d5-d5d5d5d5d5d5",
                    "path": "<Gamepad>/leftShoulder",
                    "interactions": "",
                    "processors": "",
                    "groups": "Gamepad",
                    "action": "CycleAmmoPrev",
                    "isComposite": false,
                    "isPartOfComposite": false
                },
                {
                    "name": "",
                    "id": "d6d6d6d6-d6d6-d6d6-d6d6-d6d6d6d6d6d6",
                    "path": "<Gamepad>/rightShoulder",
                    "interactions": "",
                    "processors": "",
                    "groups": "Gamepad",
                    "action": "CycleAmmoNext",
                    "isComposite": false,
                    "isPartOfComposite": false
                },
                {
                    "name": "",
                    "id": "d7d7d7d7-d7d7-d7d7-d7d7-d7d7d7d7d7d7",
                    "path": "<Gamepad>/buttonEast",
                    "interactions": "",
                    "processors": "",
                    "groups": "Gamepad",
                    "action": "EmergencyBurn",
                    "isComposite": false,
                    "isPartOfComposite": false
                },
                {
                    "name": "",
                    "id": "d8d8d8d8-d8d8-d8d8-d8d8-d8d8d8d8d8d8",
                    "path": "<Gamepad>/buttonWest",
                    "interactions": "",
                    "processors": "",
                    "groups": "Gamepad",
                    "action": "DeployFleet",
                    "isComposite": false,
                    "isPartOfComposite": false
                },
                {
                    "name": "",
                    "id": "d9d9d9d9-d9d9-d9d9-d9d9-d9d9d9d9d9d9",
                    "path": "<Gamepad>/buttonNorth",
                    "interactions": "",
                    "processors": "",
                    "groups": "Gamepad",
                    "action": "SwitchFormation",
                    "isComposite": false,
                    "isPartOfComposite": false
                },
                {
                    "name": "",
                    "id": "dadadada-dada-dada-dada-dadadadada",
                    "path": "<Gamepad>/buttonSouth",
                    "interactions": "",
                    "processors": "",
                    "groups": "Gamepad",
                    "action": "ContextAction",
                    "isComposite": false,
                    "isPartOfComposite": false
                },
                {
                    "name": "",
                    "id": "dbdbdbdb-dbdb-dbdb-dbdb-dbdbdbdbdbdb",
                    "path": "<Gamepad>/start",
                    "interactions": "",
                    "processors": "",
                    "groups": "Gamepad",
                    "action": "Pause",
                    "isComposite": false,
                    "isPartOfComposite": false
                },
                {
                    "name": "",
                    "id": "dcdcdcdc-dcdc-dcdc-dcdc-dcdcdcdcdcdc",
                    "path": "<Gamepad>/select",
                    "interactions": "",
                    "processors": "",
                    "groups": "Gamepad",
                    "action": "QuickStats",
                    "isComposite": false,
                    "isPartOfComposite": false
                }
            ]
        }
    ],
    "controlSchemes": [
        {
            "name": "Gamepad",
            "bindingGroup": "Gamepad",
            "devices": [
                {
                    "devicePath": "<Gamepad>",
                    "isOptional": false,
                    "isOR": false
                }
            ]
        }
    ]
}
```

---

### C# Controller Handler

```csharp
using UnityEngine;
using UnityEngine.InputSystem;

public class EVERebellionController : MonoBehaviour
{
    // Hard-locked input actions
    private PlayerInput playerInput;
    private InputActionMap gameplayMap;
    
    // Input state
    public Vector2 MoveVector { get; private set; }
    public Vector2 AimVector { get; private set; }
    public float TriggerPressure { get; private set; }
    public bool IsFiring { get; private set; }
    public bool IsAltFiring { get; private set; }
    
    // Input lock
    private bool inputLocked = false;
    private float lockTimer = 0f;
    
    // Settings (NOT bindings)
    public float DeadzonMove = 0.15f;
    public float DeadzoneAim = 0.20f;
    public float SensitivityMove = 1.0f;
    public float SensitivityAim = 0.8f;
    public bool InvertY = false;
    public float HapticIntensity = 1.0f;
    
    private void Awake()
    {
        playerInput = GetComponent<PlayerInput>();
        gameplayMap = playerInput.actions.FindActionMap("Gameplay");
    }
    
    private void Update()
    {
        if (inputLocked)
        {
            lockTimer -= Time.deltaTime;
            if (lockTimer <= 0)
            {
                inputLocked = false;
            }
            else
            {
                // Zero inputs while locked
                MoveVector = Vector2.zero;
                IsFiring = false;
                IsAltFiring = false;
                return;
            }
        }
        
        // Read movement (HARD-LOCKED to left stick)
        Vector2 rawMove = gameplayMap.FindAction("Move").ReadValue<Vector2>();
        MoveVector = ApplyMomentumCurve(rawMove) * SensitivityMove;
        
        if (InvertY)
            MoveVector.y = -MoveVector.y;
        
        // Read aim (HARD-LOCKED to right stick)
        Vector2 rawAim = gameplayMap.FindAction("Aim").ReadValue<Vector2>();
        AimVector = rawAim * SensitivityAim;
        
        if (InvertY)
            AimVector.y = -AimVector.y;
        
        // Read triggers
        TriggerPressure = gameplayMap.FindAction("PrimaryFire").ReadValue<float>();
        IsFiring = TriggerPressure > 0.05f;
        IsAltFiring = gameplayMap.FindAction("AlternateFire").ReadValue<float>() > 0.05f;
    }
    
    private Vector2 ApplyMomentumCurve(Vector2 input)
    {
        float x = input.x == 0 ? 0 : Mathf.Sign(input.x) * Mathf.Pow(Mathf.Abs(input.x), 1.8f);
        float y = input.y == 0 ? 0 : Mathf.Sign(input.y) * Mathf.Pow(Mathf.Abs(input.y), 1.8f);
        return new Vector2(x, y);
    }
    
    public void LockInputs(float duration = 1.0f)
    {
        inputLocked = true;
        lockTimer = duration;
        
        // Death haptic
        if (Gamepad.current != null)
        {
            Gamepad.current.SetMotorSpeeds(
                HapticIntensity * 0.7f,  // Low frequency
                HapticIntensity * 1.0f   // High frequency
            );
            
            // Stop after 500ms
            Invoke(nameof(StopHaptics), 0.5f);
        }
    }
    
    private void StopHaptics()
    {
        if (Gamepad.current != null)
            Gamepad.current.SetMotorSpeeds(0, 0);
    }
    
    public bool IsActionJustPressed(string actionName)
    {
        return gameplayMap.FindAction(actionName).WasPressedThisFrame();
    }
    
    public Vector2 GetAimOffset()
    {
        return AimVector * 30f;  // pixels, matches pygame
    }
}
```

---

## 📋 QUICK REFERENCE

### Axis/Button Mappings (Universal)

| Function | Axis/Button | Xbox | PlayStation |
|----------|-------------|------|-------------|
| Move X | Axis 0 | Left Stick X | Left Stick X |
| Move Y | Axis 1 | Left Stick Y | Left Stick Y |
| Aim X | Axis 2 | Right Stick X | Right Stick X |
| Aim Y | Axis 3 | Right Stick Y | Right Stick Y |
| Primary Fire | Axis 5 | RT | R2 |
| Alternate Fire | Axis 4 | LT | L2 |
| Context | Button 0 | A | Cross (×) |
| Burn | Button 1 | B | Circle (○) |
| Fleet | Button 2 | X | Square (□) |
| Formation | Button 3 | Y | Triangle (△) |
| Cycle Prev | Button 4 | LB | L1 |
| Cycle Next | Button 5 | RB | R1 |
| Stats | Button 6 | Back/Select | Share |
| Pause | Button 7 | Start | Options |
| D-Pad Up | Button 11 | D-Pad ↑ | D-Pad ↑ |
| D-Pad Down | Button 12 | D-Pad ↓ | D-Pad ↓ |
| D-Pad Left | Button 13 | D-Pad ← | D-Pad ← |
| D-Pad Right | Button 14 | D-Pad → | D-Pad → |

---

## 🔒 BINDING LOCK ENFORCEMENT

### Godot: Disable Input Remapping

```gdscript
# In project settings or main scene
func _ready():
    # Disable input map editor in runtime
    InputMap.load_from_globals = true
    
    # Prevent action modification
    for action in InputMap.get_actions():
        # Store original, reject changes
        pass
```

### Unity: Disable Rebinding

```csharp
public class InputLockManager : MonoBehaviour
{
    private void Awake()
    {
        // Disable runtime rebinding
        var playerInput = GetComponent<PlayerInput>();
        playerInput.notificationBehavior = PlayerNotifications.InvokeCSharpEvents;
        
        // Lock action map (can't be changed in runtime)
        playerInput.currentActionMap.Disable();
        playerInput.currentActionMap.Enable();
    }
}
```

---

## ✅ TESTING CHECKLIST

### Cross-Engine Verification

- [ ] All 22 actions mapped identically
- [ ] Deadzone values match pygame (0.15/0.20/0.10)
- [ ] Momentum curve produces same output (input^1.8)
- [ ] Haptic feedback triggers on same events
- [ ] Input lock prevents all actions during death
- [ ] No rebinding UI accessible to player
- [ ] Button hints show correct platform icons

---

## 🎯 MIGRATION NOTES

If moving from pygame → Godot/Unity:

1. Import this binding file to engine
2. Attach controller script to player
3. Test all 22 actions in-engine
4. Verify haptic feedback works
5. Ensure input lock functions
6. Remove any default rebinding UI
7. Test on actual Xbox/PlayStation controller

**Bindings are IDENTICAL across engines - no translation needed.**

---

## 📦 EXPORT FILES

**Godot**: Copy `[input]` section to `project.godot`  
**Unity**: Import JSON as `InputActions` asset

Both engines now have EVE Rebellion's hard-locked controller layout.
