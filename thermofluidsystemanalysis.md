---
layout: project
title: "Thermofluid System Analysis"
description: "We analyzed a thermodynamic cycle using an engine."
images:/assets/images/stroke.jpeg
 
---

We were asked to create an analysis of a thermodynamic cycle, so we decided to use an engine for this project.

In this project, we modeled and analyzed a thermodynamic cycle using MATLAB and SolidWorks. We examined key parameters such as temperature, pressure, and efficiency. The goal was to understand the performance of the system and optimize the design for practical applications.

Engine:


1. Intake:
Intake valve, piston moves down and an air-fuel mixture enter

2. Compression:
Piston moves up and the air-fuel mixture is compressed, T and P increase

3. Power:
Spark ignites the mixture, combustion increases P, expanding gas pushes piston creating work

4. Exhaust:
Valve opens and piston pushes exhaust gases out.

⸻

3.

Air + fuel → | piston | → Exhaust valve
spark plug
valve

ṁ_in = ṁ_out
dm/dt = 0

⸻

4A.

ΔS_sys = 0

= ∫(δQ_rev / T) + σ

σ = − ∫(δQ_rev / T)

Main sources of entropy generation:
	•	Combustion irreversibility
	•	Finite heat transfer
	•	Friction

Minimizing entropy change will increase useful work.

⸻

4B.

ΔU = Q − W
Steady state

ΔU = 0

W_out = Q_in − Q_out

Q_in = m c_v (T₃ − T₂)
Q_out = m c_v (T₄ − T₁)

→ W = m c_v (T₃ + T₁ − T₄ − T₂)

W_net = ṁ_fuel (η_engine)

⸻

4C.

η = 1 − (Q_out / Q_in) = 1 − (T₄ − T₁) / (T₃ − T₂)

⸻

5. Increase efficiency of engine

If efficiency increases, T₃ − T₂ must increase

Knock (autoignition): Increasing r raises cylinder temperature and pressure during compression so there is less high quality

Mechanical stress / durability: Higher pressures raise peak mechanical loads on pistons which means more expensive and higher quality materials

Real efficiency vs ideal: Real engines have friction, pumping losses, non-ideal combustion, and heat transfer losses, which makes the real engine much less efficient

Alternative approach — turbocharging: Instead of increasing static compression ratio, many engines use a boosted intake (turbo/supercharging) to increase the ṁ_dot. Turbocharging increases power and can increase thermal efficiency at part load, but it increases intake temperature.
