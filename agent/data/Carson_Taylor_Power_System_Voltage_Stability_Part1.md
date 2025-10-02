# Power System Voltage Stability - Part 1: Introduction and Basic Concepts
**Source**: carson-w-taylor-power-system-voltage-stability-1994pdf
**Type**: Technical Manual  
**Domain**: Power Systems Engineering
**Topic**: Voltage Stability, Power System Analysis, Reactive Power Control
**Author**: Carson W. Taylor
**Publisher**: McGraw-Hill, Inc.
**Year**: 1994

## Preface

Power transmission capability has traditionally been limited by either rotor angle (synchronous) stability or by thermal loading capabilities. The blackout problem has been associated with transient stability; fortunately this problem is now diminished by fast short circuit clearing, powerful excitation systems, and various special stability controls. Voltage (load) stability, however, is now a major concern in planning and operating electric power systems. More and more electric utilities are facing voltage stability-imposed limits. Voltage instability and collapse have resulted in several major system failures (blackouts) such as the massive Tokyo blackout in July 1987. Voltage stability will remain a challenge for the foreseeable future and, indeed, is likely to increase in importance.

One reason is the need for more intensive use of available transmission facilities. The increased use of existing transmission is made possible, in part, by reactive power compensation—which is inherently less robust than "wire-in-the-air." Over the last ten to fifteen years, and especially over about the last five years, utility engineers, consultants, and university researchers have intensely studied voltage stability. Hundreds of technical papers have resulted, along with many conferences, symposiums, and seminars. Utilities have developed practical analysis techniques, and are now planning and operating power systems to prevent voltage instability for credible disturbances. All relevant phenomena, including longer-term phenomena, can be demonstrated by time domain simulation. While experts now have a good understanding of voltage phenomena, a comprehensive, practical explanation of voltage stability in book form is necessary. This is the first book on voltage stability.

Power System Voltage Stability is an outgrowth of many two-three day seminars which I began offering in 1988. As a full-time engineer of the Bonneville Power Administration (BPA), the book is influenced by my work on voltage stability problems in the Pacific Northwest and adjacent areas. It is also influenced by my participation in voltage stability work of the Western Systems Coordinating Council, North American Electric Reliability Council, IEEE, CIGRE, and EPRI. Although voltage stability is fairly well understood, there are many facets to the problem, ranging from generator controls to transmission network reactive power compensation to distribution network design to load characteristics. The physical characteristics and mathematical models of a wide range of equipment are important.

Power System Voltage Stability emphasizes the physical or engineering aspects of voltage stability, providing a conceptual understanding of voltage stability. The simplest possible models are used for conceptual explanations. Practical methods for computer analysis are emphasized. We aim to develop good intuition relative to voltage problems, rather than to describe sophisticated mathematical analytical methods. The book is primarily for practicing engineers in power system planning and operation. However, the book should be useful to university students as a supplementary text. University researchers may find the book provides necessary background material on the voltage stability problem. Many references are provided for those who wish to delve deeper into a fascinating subject. The references are not exhaustive, however, and generally represent recent publications which build on earlier work. In keeping with the intended audience, most of the references are quite readable by those without advanced mathematical training.

### Outline of Book

The book is divided into nine chapters and six appendices. Chapter 1 is introductory with emphasis on reactive power transmission. Chapter 2 introduces the subject of voltage stability, providing definitions and basic concepts. Voltage stability is separated into transient and longer-term phenomena.

Chapters 3-5 describe equipment characteristics for transmission systems, generation systems, and distribution/load systems. Modeling of equipment is emphasized. Chapters 6 and 7 describe computer simulation examples for both small equivalent power systems and for a very large power system. Both static and dynamic simulation methods are used. Both transient and longer-term forms of voltage stability are studied using conventional and advanced computer programs. Chapter 8 describes voltage stability associated with HVDC links. Here the reactive power demand of HVDC inverters is important. Chapter 9 provides planning and operating guidelines, and potential solutions to voltage problems.

The appendices include description of computer methods for power flow and dynamic simulation, and description of voltage instability incidents. Voltage stability is still a fresh subject and many advances in understanding, simulation software, and on-line security assessment software will be made in future years. In fact, the book was frequently updated until the submission deadline. It's likely that a revised edition will be called for.

## Chapter 1: General Aspects of Electric Power Systems

Everything you know is easy. Serbian saying

Power system voltage stability involves generation, transmission, and distribution. Voltage stability is closely associated with other aspects of power system steady-state and dynamic performance. Voltage control, reactive power compensation and management, rotor angle (synchronous) stability, protective relaying, and control center operations all influence voltage stability. Before introducing voltage stability in the next chapter, we review aspects of power system engineering important to power system planning and operating engineers.

### 1.1 Brief Survey of Power System Analysis and Operation

In this book, our overriding concern is power system security. We must avoid failures and blackouts of the bulk power delivery system. Economic system operation is of secondary importance during emergency conditions, but is important during normal conditions. In system design and operation we need a balance between economy and security.

**Disturbances**. A large interconnected power system is exposed to many disturbances which threaten security. Recent requirements for more intensive use of available generation and transmission have magnified the possible effects of these disturbances.

For three-phase power systems, the disturbances can be divided into balanced and unbalanced disturbances. Unbalanced disturbances are normally caused by short circuits (faults) affecting only one or two of the phases; faults involving ground are the most common. Balanced disturbances result from transmission line and generation outages, and from load changes. Following any disturbance, electromechanical oscillations occur between generators.

**Computer simulation programs**. Large-scale computer simulation programs for studying power system steady-state and dynamic performance include short circuit programs, power flow programs, small-signal stability (eigenvalue) programs, transient stability programs, and longer-term dynamics programs. Power flow programs are basic to power system analysis, planning, and operation. Similar network power flow computation techniques are used in other software for optimal power flow, dynamic simulation, on-line security assessment, and state estimation. Power flow programs normally represent the generation and transmission systems in the sinusoidal fundamental-frequency steady-state under balanced conditions. Loads are usually lumped at bulk power delivery substation busses. A solved case provides the voltage magnitudes and angles at each bus, and the real and reactive power flows. Appendix B describes the power flow problem.

Time domain transient stability programs are used to determine rotor angle synchronous stability performance—both the "first swing" and subsequent transient damping. The dynamic performance of induction motors and various controls can also be evaluated. Numerical integration is the computation method. Eigenvalue and related methods are also useful in evaluating electromechanical stability of linearized systems—damping of low-frequency oscillations and the effects of controls are often studied. These subjects are described in depth in the companion book Power System Stability and Control by Dr. Prabha Kundur.

Longer-term dynamics programs evaluate slower dynamics. These programs are discussed later chapters and in Appendix D.

**Controls**. Various power system controls—local and centralized—are important in voltage stability. The local controls, particularly at generating plants, are automatic and relatively high speed. Direct and indirect control of loads are critical for voltage stability. Each company or control area has a central control or dispatch center where slower automatic and manual control commands are issued to power plants and substations. The primary centralized automatic control is Automatic Generation Control (AGC). Centralized voltage control usually has a "man-in-the-loop." Other than telephone communication, there is seldom central control at the synchronous interconnection level.

**Large-scale systems**. Electric power systems are the largest man-made dynamic systems on earth. Networks comprise thousands of nodes and the significant dynamics are equivalent to thousands of first-order nonlinear differential equations. At any instant in time, generation must match load. Generators thousands of kilometers apart connected by highly-loaded transmission circuits must operate in synchronism. This must be done reliably through the daily load cycle and for disturbance conditions.

Electric power systems are comprised of generation, transmission, and distribution/loads. These three subsystems must operate together as an overall system. We must understand each subsystem. Equally important, we must understand how they relate; this system engineering is shown by the intersection areas of Figure 1-1. Voltage stability is only one aspect of power system engineering. But it is a very interesting one!

### 1.2 Active Power Transmission using Elementary Models

In this section and the next, we review the basics of electric power transmission. To facilitate understanding, we use simple models. Once basic concepts are understood, we can represent as much detail as appropriate in computer simulation.

Active (real) and reactive power transmission depend on the voltage magnitude and angles at the sending and receiving ends. Figure 1-2 shows our model; synchronous machines are indicated at both ends. The sending- and receiving-end voltages are assumed fixed and can be interpreted as points in large systems where voltages are stiff or secure. The sending and receiving ends are connected by an equivalent reactance.

The relations can be easily calculated:

```
S_s = P_s + jQ_s = E_s I_s* = (E_s/X)[E_s sin δ + j(E_s cos δ - E_r)]
```

```
P_s = (E_s E_r / X) sin δ = P_max sin δ                                    (1.1)
```

```
Q_s = (E_s E_r cos δ - E_s²) / X                                          (1.2)
```

Similarly, for the sending end:

```
P_r = (E_s E_r / X) sin δ = P_max sin δ                                   (1.3)
```

```
Q_r = (E_r² - E_s E_r cos δ) / X                                          (1.4)
```

The familiar equations for P_s and P_r are equal because we have a lossless system; maximum power transfer is at a power or load angle δ equal to 90°. Figure 1-3 shows the plot of Equation 1.1 or 1.3, termed the power-angle curve. The 90° maximum power angle is nominal—maximum power occurs at a different angle if we included transmission losses or resistive shunt loads. In the next chapter, we will describe the case where the receiving end is an impedance load.

Also shown on Figure 1-3 is a load line representing constant sending end mechanical (turbine) power. The stable intersection of the mechanical power and the electrical power-angle curve is on the left at an angle less than 90°. The right side intersection is unstable.

To understand this, let the receiving-end system be very large, an infinite bus with fixed angle and speed. A small increase in mechanical power at the sending-end generator (by opening the steam valves or water gates) accelerates the generator, thereby increasing the angle. The increased angle results in less electrical power which further accelerates the generator and further increases the angle. On the left-side intersection, however, the increased angle increases the electrical power to match the increased mechanical power.

For typical power transfers and power angles, say up to 30°, we can linearize Equations 1.1 and 1.3 by the relation sin δ ≈ δ with δ in radians. (For example, thirty degrees is 0.5236 radians and sin 30° = 0.5; note the nearly linear relationship for small angles on Figure 1-3.) We then write:

P = P_max δ

and state: Real or active power transfer depends mainly on the power angle.

To insure steady-state rotor angle (synchronous) stability, angles across a transmission system are usually kept below about 44°.

### 1.3 Reactive Power Transmission using Elementary Models

In this book, we are especially interested in the transmission of reactive power. First, we can return to the power-angle curve and note that the reactive requirements of the sending and receiving ends are excessive at high angles and correspondingly high real power transfers. Making the assumption that E_s = E_r, Figure 1-4 shows a plot for Q_s = -Q_r. At the 90° steady-state stability limit, the reactive power that must be generated at the two sources is equal to P_max. (Referring to Figure 1-2, part of the reactive power is provided by transmission line capacitance).

Usually we are interested in variable voltage magnitudes. Particularly, we are interested in the reactive power that can be transmitted across a transmission line, a transmission line equivalent, or a transformer as the receiving- or load-end voltage sags during a voltage emergency or collapse. Referring to Figure 1-2, we now consider reactive power flow over the transmission line alone and rewrite Equations 1.2 and 1.4 in terms of V_s∠θ_s and V_r∠θ_r. Also, X now represents the transmission line reactance alone.

```
Q_s = (V_s V_r cos θ - V_r²) / X                                          (1.5)
```

```
Q_r = (V_s² - V_s V_r cos θ) / X                                          (1.6)
```

We can write approximate formulas for small angles by using cos θ ≈ 1:

```
Q_s = V_s(V_s - V_r) / X                                                  (1.7)
```

```
Q_r = V_r(V_r - V_s) / X                                                  (1.8)
```

From Equations 1.7-1.8, we state: Reactive power transmission depends mainly on voltage magnitudes and flows from the highest voltage to the lowest voltage.

Also:
- P and δ are closely coupled, and
- Q and V are closely coupled.

These physical relationships are taken advantage of in computer algorithms, notably the fast decoupled power flow (Appendix B). Next, we examine how these relationships break down during high stress, i.e., high power transfers and angles. This is important since voltage stability problems normally occur during highly stressed conditions (usually following outages).

**Example 1-1**. First let's simply calculate Q_s and Q_r using Equations 1.5 and 1.6 for an angle of 30°. Let V_s be 1 per unit and let V_r be 0.9 per unit. We have a substantial voltage gradient of 10% between the two ends and we might expect large reactive power transfer. We calculate:

cos 30° = 0.866

```
Q_s = (1² - 1 × 0.9 × 0.866) / X = 0.22 / X
```

```
Q_r = (1 × 0.9 × 0.866 - 0.9²) / X = -0.03 / X
```

We have a problem! Although lots of reactive power is going into the line, nothing is coming out. The negative value means, in fact, that the line is demanding reactive power of 0.03/X pu from the receiving end. The transmission line has become a drain on the transmission system. The transmission line reactive loss is the sum of the reactive powers going into the line or 0.25/X pu.

**Power circle diagrams**. P, Q circle diagrams are a more general and precise way of understanding power transmission limitations. Circle diagrams were widely used prior to digital computer power flow programs, and are described in several textbooks on power system analysis and in the Westinghouse T&D book. The next example demonstrates this method.

**Example 1-2**. A 500-kV transmission line is 161 km (100 miles) long. We include the line shunt capacitance using a pi transmission line model. For simplicity, and with little error, we can let the line be lossless. Corresponding to an actual Bonneville Power Administration line with three subconductor per phase, the total series reactance is 51.6 ohms and the total shunt susceptance is 809 microsiemens (micromhos). In per unit on a 500-kV and 1000 MVA base, the reactance and susceptance parameters are 0.2064 per unit and 0.2023 per unit, respectively. (One thousand megawatts is approximately the 500-kV line natural or surge impedance loading and is a convenient power base; the impedance base is 250 ohms which is approximately the surge impedance.)

Using ABCD generalized circuit constants for the pi model, the parameters are:

```
A = D = 1 - YZ/2 = 0.9791 pu
B = Z = j0.2064
C = Y(1 + YZ/4) = j0.2002
```

We consider two cases: Case 1 has V_s = 1 per unit and V_r = 0.95 per unit; Case 2 has V_s = 1 per unit and V_r = 0.9 per unit. Because the line is lossless, the center of all sending- and receiving-end circles are on the vertical reactive power axis. The two cases result in two sending end and two receiving circles. The circle centers and radii (same for both sending and receiving ends) are:

```
Center_s case 1 = V_s²/B = j4.7437 pu
Center_r case 1 = -V_r²/B = -j4.2812 for V_r = 0.95 pu
Center_r case 2 = -V_r²/B = -j3.8451 pu for V_r = 0.9 pu

Radius = V_s V_r/B = 4.6028 pu for V_r = 0.95 pu
Radius = V_s V_r/B = 4.3605 pu for V_r = 0.9 pu
```

Figure 1-5 shows the power circle curves. The solid circles are for Case 1 and the dashed circles are for Case 2. For any specified real power transfer, we can draw a vertical line. The intersection of the vertical line and a circle gives reactive power. Also, for a specified real power, the angle between the vertical axis and a line drawn from a circle center to the point on the circle is the power angle θ.

Concentrating on the receiving-end circles, we clearly see when reactive power becomes negative—and the transmission line becomes a drain on the receiving-end system. For V_r = 0.95 per unit, the power value is about 1700 MW. For V_r = 0.9 per unit, the power value is about 2250 MW. We also note the high reactive power requirements from the sending- and receiving-end systems at very high real power transfers. The corresponding angles can be determined graphically or analytically (Equation 1.1). At high loadings the curves become steep, meaning that more than one megavar is required for each additional megawatt transmitted.

The same method can be used for series/parallel combinations of transmission lines. Generalized circuit constants (ABCD constants) facilitate converting the lines to a single pi equivalent.

### 1.4 Difficulties with Reactive Power Transmission

The last section hinted at one difficulty with reactive power transmission: Reactive power cannot be transmitted across large power angles even with substantial voltage magnitude gradients. High angles are due to long lines and high real power transfers. Requirements to maintain voltage magnitude profiles with voltages of approximately 1 per unit ± 5% contribute to the difficulty. Contrasted with real power transfers, reactive power simply cannot be transmitted long distances.

There are other reasons to minimize transfer of reactive power. Minimizing real and reactive losses is a second reason. Real losses should be minimized for economic reasons; reactive losses should be minimized to reduce investment in reactive power devices such as shunt capacitors. The losses across the series impedance of a transmission line are I²R and I²X. For I², we can write:

```
I² = |S|²/V² = (P² + Q²)/V²
```

and

```
P_loss = I²R = (P² + Q²)/V² × R                                           (1.10)
```

```
Q_loss = I²X = (P² + Q²)/V² × X                                           (1.11)
```

To minimize losses, we must minimize reactive power transfer. We should also keep voltages high. Keeping voltages high to minimize reactive losses helps maintain voltage stability.

Minimizing temporary overvoltage due to "load rejection" is a third reason. The most onerous case is opening the receiving-end circuit breakers with the transmission line still energized from the sending end. Figure 1-6 shows an equivalent system and an even simpler thévenin circuit. Also shown is the resulting phasor diagram. Prior to the breaker opening, the thévenin voltage is:

```
E_th ∠δ = V ∠0 + jXI = V + jX(P - jQ)/V = V + j(XQ/V) + (XP/V)           (1.12)
```

From the equation and phasor diagram, we note that the voltage rise term in phase with V depends on Q. This term mainly determines E_th (the thévenin voltage magnitude). The angle, δ, depends mainly on the quadrature term involving P.

What happens when the breaker is opened? What does the voltage at the open end of the line become? Clearly, the current goes to zero and the voltage becomes E_th. Thus the temporary overvoltage is largely determined by the reactive power transfer. Two examples will show this.

**Example 1-3**. A 100 km, 500-kV line has a series reactance of X = 0.35 Ω/km. The power transmitted is 1000 MW or 1 per unit. The impedance base is 250 ohms and the transmission line reactance is 0.14 per unit. At the source end, the short circuit capacity is 5000 MW or 5 per unit; the corresponding source reactance is 1/5 or 0.2 per unit. The total reactance is 0.34 per unit. The line is relatively short but the source is relatively weak. Let V = 1 per unit. Consider two cases: unity power factor load and 0.85 power factor load.

Case 1: cos φ = 1, Q_s = 0,

```
E_th ∠δ = 1 + j0.34 × 1 = 1.056 ∠18.8°
```

Case 2: cos φ = 0.85, Q_s = P_s tan φ = 0.62 pu,

```
E_th ∠δ = 1 + j(0.34 × 0.62) + j(0.34 × 1) = 1.211 + j0.341 = 1.258 ∠15.7°
```

The delivery of 0.62 pu reactive power has increased the fundamental frequency load rejection overvoltage from 1.056 per unit to 1.258 per unit. The next example is more dramatic.

**Example 1-4**. This example involves a high voltage direct current (HVDC) transmission link connected to a weak power system. The thévenin reactance is 0.625, corresponding to the inverse of the "effective short circuit ratio" (ESCR) which is 1.6. Several existing HVDC links have such a high network reactance. HVDC converters consume reactive power of 50-60% of the dc power. Let the dc power be 1 per unit and the reactive consumption be 0.6 per unit; also, let the converter commutating bus voltage be 1 per unit. See Figure 1-7.

Using Equation 1.12, the thévenin voltage is:

```
E_th ∠δ = 1 + j(0.625 × 0.6) + j(0.625 × 1) = 1.375 + j0.625 = 1.51 ∠24°
```

For dc shutdown or blocking, the ac side voltage will jump to an intolerable level of 1.51 per unit! Measures must be taken to prevent such a high load rejection voltage. (One measure would be to produce the reactive power locally with a synchronous condenser—this increases the effective short circuit capacity and correspondingly reduces the thévenin reactance.)

Note that if the dc converter is an inverter, the same problem occurs; only the signs of the dc power and of the thévenin angle are changed. Rectifiers and inverters consume similar amounts of reactive power.

Whenever possible, reactive power should be generated close to the point of consumption. We can list several reasons to minimize reactive power transfer:

1. It is inefficient during high real power transfer and requires substantial voltage magnitude gradients.
2. It causes high real and reactive power losses.
3. It can lead to damaging temporary overvoltages following load rejections.
4. It requires larger equipment sizes for transformers and cables.

### 1.5 Short Circuit Capacity, Short Circuit Ratio, and Voltage Regulation

We now discuss some terms used in the previous section. These are useful in describing the voltage (as opposed to mechanical or inertial) strength of a network. The concepts are useful for simple calculations prior to computer studies.

**Short circuit capacity**. The short circuit capacity or power of a network is the product of three-phase fault current and rated voltage. In physical units, with short circuit current in kiloamperes and phase-to-phase voltage in kilovolts, the short circuit capacity is:

```
S_sc = √3 × V × I_sc MVA
```

We, however, will generally use per unit quantities. The short circuit capacity is then simply the product of voltage (usually one per unit) and fault current. The fault current is usually considered to be rated (one per unit) voltage divided by the impedance or reactance to the fault location. With one per unit voltages, the short circuit capacity is then the system admittance (or susceptance), or the inverse of the system thévenin impedance (or reactance).

The short circuit capacity and thévenin impedance can be computed with a short circuit program. A transient stability program can also be used by applying a three-phase fault and noting the initial current flow to the fault point.

The short circuit capacity measures the system voltage strength. A high capacity (and corresponding low impedance) means the network is strong or stiff. Switching on a load, or a shunt capacitor or reactor, will not change the voltage magnitude very much. A low short circuit capacity means the network is weak.

**Short circuit ratio (SCR)**. We sometimes wish to compare the size of equipment to the strength of the power system. The equipment could be a load (such as a large motor), an HVDC converter, or a static var compensator. A simple comparison is to divide the system strength by the device size. Comparing a 1000 MW HVDC converter to 5000 MVA short circuit capacity power system results in a short circuit ratio of 5000/1000 or 5. A high short circuit ratio means good performance. A low short circuit ratio means trouble: for example, a large motor connected to a weak point on the network may stall or have difficulty reaccelerating following faults. Motor starting will cause system voltage dips.

A related term, used especially with HVDC, is effective short circuit ratio (ESCR). The basic SCR accounts for only the network strength while ESCR accounts for shunt reactive equipment at the device location. A synchronous condenser clearly increases the fault current and therefore the effective short circuit capacity. On the other hand, shunt capacitors and harmonic filters (which are capacitive at fundamental frequency) reduce the ESCR.

Short circuit capacity related measures do not account for the fast-acting controls of static var compensators, generator voltage regulators, and HVDC converters. Methods which include control effects are described in Chapter 8.

**Voltage regulation**. Several widely used approximate formulas involve system short circuit capacity. The formulas provide the voltage deviation for switching shunt reactive equipment. They are:

```
ΔV = ΔQ / S_sc                                                            (1.13)
```

and

```
V = E - jXI                                                               (1.14)
```

**Example 1-5**. A 200-MVAr capacitor is switched at a bus with 10,000 MVA short circuit capacity. The expected voltage change is 200/10,000 or 2%. This approximate result can be checked by computer power flow or stability simulation.

**Example 1-6**. A bus experiences ±3% voltage fluctuations. The short circuit capacity is 5000 MVA. We wish to size a static var compensator (SVC) to smooth the voltage fluctuations. Using Equation 1.13, we can write: ΔQ = S_sc ΔV. The approximate SVC size is then ±150 MVAr.

Equation 1.14 approximates an even simpler equation expressing the voltage drop from the source to load point. That is: V = E - jXI. Figure 1-8 is a plot of Equation 1.14 and shows the system voltage/reactive characteristic or load line. The slope of the load line is related to the system stiffness—a nearly flat slope means a strong system.

The voltage/reactive characteristics of shunt reactive devices (capacitor, reactor, or static var compensator) can be superimposed on the system characteristic. In the next chapter, we introduce V-Q curves produced by computer power flow simulation. The system characteristic will not be linear at high inductive loading. The dashed portion of Figure 1-8 gives a hint of voltage problems.

## Chapter 2: What is Voltage Stability?

Make everything as simple as possible, but not more so. A. Einstein

We now introduce voltage stability, the subject of this book. First, we present some definitions. Then, we describe voltage instability mechanisms and the relation with rotor angle stability. Next, we discuss the reasons for voltage stability problems in mature power systems. We finish by introducing static voltage stability analysis using P-V and V-Q curves.

### 2.1 Voltage Stability, Voltage Collapse, and Voltage Security

Voltage stability covers a wide range of phenomena. Because of this, voltage stability means different things to different engineers. It's a fast phenomenon for engineers involved with induction motors, air conditioning loads, or HVDC links. It's a slow phenomenon (involving, for example, mechanical tap changing) for other engineers. Engineers and researchers have discussed appropriate analysis methods, with debate on whether voltage stability is a static or dynamic phenomenon.

Voltage instability and voltage collapse are used somewhat interchangeably by most engineers. Voltage stability or voltage collapse has often been viewed as a steady-state "viability" problem suitable for static (power flow) analysis. The ability to transfer reactive power from production sources to consumption sinks during steady operating conditions is a major aspect of voltage stability. A 1987 CIGRE report recommends analysis methods and power system planning approaches based on static models.

The network maximum power transfer limit is not necessarily the voltage stability limit. Voltage instability or collapse is a dynamic process. The word "stability" implies a dynamic system. A power system is a dynamic system. We will see that, in contrast to rotor angle (synchronous) stability, the dynamics mainly involves the loads and the means for voltage control. Voltage stability has been called load stability.

**Definitions**. Voltage stability is a subset of overall power system stability. We adopt definitions developed by CIGRE. The definitions are based on reference 4 and are in the spirit of references 5-7. The stability definitions are analogous to stability definitions for other dynamic system. Our definitions are:

A power system at a given operating state is small-disturbance voltage stable if, following any small disturbance, voltages near loads are identical or close to the pre-disturbance values. (Small-disturbance voltage stability corresponds to a related linearized dynamic model with eigenvalues having negative real parts. For analysis, discontinuous models for tap changers may have to be replaced with equivalent continuous models.)

A power system at a given operating state and subject to a given disturbance is voltage stable if voltages near loads approach post-disturbance equilibrium values. The disturbed state is within the region of attraction of the stable post-disturbance equilibrium.

A power system at a given operating state and subject to a given disturbance undergoes voltage collapse if post-disturbance equilibrium voltages are below acceptable limits. Voltage collapse may be total (blackout) or partial.

Voltage instability is the absence of voltage stability, and results in progressive voltage decrease (or increase). Destabilizing controls reaching limits, or other control actions (e.g., load disconnection), however, may establish global stability.

Voltage stability normally involves large disturbances (including rapid increases in load or power transfer). Furthermore the instability is almost always an aperiodic decrease in voltage. Oscillatory voltage instability may be possible, but control instabilities are excluded. Control instabilities could occur, for example, because of too high a gain on a static var compensator or too small a deadband in a voltage relay controlling a shunt capacitor bank.

Overvoltage phenomena and instability such as self-excitation of rotating machines are outside the scope of the definitions. Overvoltages are normally more of an equipment problem than a power system stability problem.

The term voltage security is used. This means the ability of a system, not only to operate stably, but also to remain stable following credible contingencies or load increases. It often means the existence of considerable margin from an operating point to the voltage instability point (or to the maximum power transfer point) following credible contingencies.

Although voltage stability involves dynamics, power flow based static analysis methods are often useful for rapid, approximate analysis.

### 2.2 Time Frames for Voltage Instability, Mechanisms

Voltage instability and collapse dynamics span a range in time from a fraction of a second to tens of minutes. Time response charts have been used to describe dynamic phenomena. Figure 2-1 shows that many power system components and controls play a role in voltage stability. Only some, however, will significantly participate in a particular incident or scenario. The system characteristics and the disturbance will determine which phenomena are important.

Figure 2-1 also shows a classification of voltage stability into transient and longer-term time frames. There is almost always a clear separation between the two time frames. Actual incidents experienced by utilities are grouped by time frame in Appendix F.

**Mechanisms—scenarios**: We now describe the two classifications of voltage instability. Only the basic ideas are described in this introduction. We describe three scenarios.

**1. Scenario 1: transient voltage stability**. The time frame is zero to about ten seconds—which is also the time frame of transient rotor angle stability. The distinction between voltage instability and rotor angle instability isn't always clear, and aspects of both phenomena may exist. Does voltage collapse cause loss of synchronism, or does loss of synchronism cause voltage collapse?

Voltage collapse is caused by unfavorable fast-acting load components such as induction motors and dc converters. For severe voltage dips (such as during slowly-cleared short circuits), the reactive power demand of induction motors increases, contributing to voltage collapse unless protection or ac contactors trip the motors. (This has also been termed induction motor instability.) Following faults, motors have difficulty reaccelerating. Stall-prone motors can cause other nearby motors to stall. In simulation studies, motors must be represented as dynamic devices. The characteristic of shunt capacitor bank compensation (reactive power proportional to the voltage squared) adds to the problems.

Electrical islanding and underfrequency load shedding studies have shown probable voltage collapse when the imbalance in the island is greater than about 50%. Voltage decays faster than frequency—the voltage decay affects voltage-sensitive loads, slowing frequency decay and delaying underfrequency load shedding. Also, underfrequency relays may not operate because of the low voltages. Undervoltage load shedding may be necessary. For an incident in Florida, Figure 2-2 shows voltage collapsing before frequency decays to the underfrequency load shedding setpoints. Induction motor loads, including power plant auxiliary motors, were important in the incident.

In recent years, the integration of high voltage direct current (HVDC) links into voltage-weak power systems has caused transient voltage stability problems. As an example, for stressed conditions and for large disturbances, simulations have shown voltage collapse tendencies in Southern California, aggravated by the two large inverter stations near Los Angeles. Sometimes (at the expense of synchronizing power) it's necessary to reduce dc power (and thereby converter reactive power demand) to support voltages. Chapter 8 describes voltage stability with HVDC links.

**2. Scenario 2: longer-term voltage stability**. The time frame is several minutes, typically two-three minutes. Operator intervention is often not possible. The terms "mid-term" stability, and "post-transient" or "post-disturbance" stability have been used.

This scenario involves high loads, high power imports from remote generation, and a sudden large disturbance. The system is transiently stable because of the voltage sensitivity of loads. The disturbance (loss of large generators in a load area or loss of major transmission lines) causes high reactive power losses and voltage sags in load areas. Tap changers on bulk power delivery LTC transformers and distribution voltage regulators sense the low voltages and act to restore distribution voltages—thereby restoring load power levels. The load restoration causes further sags of transmission voltages. Nearby generators are overexcited and overloaded, but overexcitation limiters (or power plant operators) return field currents to rated values as the time-overload capability (one to two minutes) expires. Generators farther away must then provide the reactive power. As described in Chapter 1, this is inefficient and ineffective. The generation and transmission system can no longer support the loads and the reactive losses, and rapid voltage decay ensues. Partial or complete voltage collapse follows. The final stages may involve induction motor stalling and protective relay operations. Depending on the type of loads (including means for disconnection at low voltage) the collapse may be partial or total.

**3. Scenario 3: longer-term voltage instability**. The instability evolves over a still longer time period and is driven by a very large load buildup (morning or afternoon pickup), or a large rapid power transfer increase. The load buildup, measured in megawatts/minute, may be quite rapid. Operator actions, such as timely application of reactive power equipment or load shedding, may be necessary to prevent instability. Factors such as the time-overload limit of transmission lines (tens of minutes) and loss of load diversity due to low voltage (due to constant energy, thermostatically controlled loads) may be important. The final stages of instability involve actions of faster equipment as described for scenarios 1 and 2.

There are many interactions among the various equipment (Figure 2-1) and time frames. For example, tap changer regulation of voltages will prevent loss of diversity by thermostatic regulation of constant energy loads. For another example, overexcitation limiter operation prevents normal generator voltage regulation.

### 2.3 Relation of Voltage Stability to Rotor Angle Stability

Voltage stability and rotor angle (or synchronous) stability are more or less interlinked. Transient voltage stability is often interlinked with transient rotor angle stability, and slower forms of voltage stability are interlinked with small-disturbance rotor angle stability. Often, the mechanisms are difficult to separate.

There are many cases, however, where one form of instability predominates. An IEEE report points out the extreme situations: (a) a remote synchronous generator connected by transmission lines to a large system (pure angle stability—the one machine to an infinite bus problem) and (b) a synchronous generator or large system connected by transmission lines to an asynchronous load (pure voltage stability). Figure 2-5 shows these extremes.

Rotor angle stability, as well as voltage stability, is affected by reactive power control. In particular, small-disturbance ("steady-state") instability involving aperiodically increasing angles was a major problem before continuously-acting generator automatic voltage regulators became available. We can now see a connection between small-disturbance angle stability and longer-term voltage stability: generator current limiting (say by an overexcitation limiter) prevents normal automatic voltage regulation. Generator current limiting is very detrimental to both forms of stability.

Voltage stability is concerned with load areas and load characteristics. For rotor angle stability, we are often concerned with integrating remote power plants to a large system over long transmission lines. Voltage stability is basically load stability, and rotor angle stability is basically generator stability.

In a large interconnected system, voltage collapse of a load area is possible without loss of synchronism of any generators. Transient voltage stability is usually closely associated with transient rotor angle stability. Longer-term voltage stability is less interlinked with rotor angle stability.

We can say that if voltage collapses at a point in a transmission system remote from loads, it's an angle instability problem. If voltage collapses in a load area, it's probably mainly a voltage instability problem.

### 2.4 Voltage Instability in Mature Power Systems

Voltage problems are expected in developing power systems. Likewise, voltage problems are expected following major system breakups. But why the recent concern in mature power systems?

One reason is intensive use of existing generation and transmission. This is because of difficulties in building new generation in load areas, and difficulties in building transmission lines from remotely-sited generation.

A second reason is increased use of shunt capacitor banks for reactive power compensation. Excessive use of shunt capacitor banks, while extending transfer limits, results in a voltage collapse-prone (brittle or fragile) network. Shunt capacitor bank reactive power output decreases by the square of voltage, hence the terms brittle or fragile.

Fast fault clearing, high performance excitation systems, power system stabilizers, and other controls are effective in removing transient stability-imposed transfer limits. With transient stability-imposed limits removed, either thermal capacity or voltage stability may dictate the transfer limits.

An example provides insight into how voltage instability can become a problem in mature systems.

**Example 2-1**. Figure 2-6 shows a five-line 500-kV transmission network. Transient stability is not a problem. What about thermal limits? Outage of one line requires the remaining lines to pick up only 25% of the power of the out-of-service line. Long EHV lines are typically loaded below one and one-half times surge impedance loading. Thermal limits are typically about three times surge impedance loading. Unlike developing two- or three-line transmission networks, thermal limits will seldom be limiting and transmission can be highly utilized.

Now consider the effect of the five-line transmission system on voltage stability. We are fighting a nonlinear current-squared relation (I²X series reactive power loss). Near surge impedance loading, the current in each line is 1000 amperes; a line outage will increase series reactive losses from 1200 MVAr (5 lines × 3 phases × 1000² × 80 ohms) to 1500 MVAr—an increase of 300 MVAr. Now consider several years load growth resulting in high utilization. With 1500 ampere loading, an outage increases series reactive losses from 2700 MVAr to 3375 MVAr—an increase of 675 MVAr or 225% over the surge impedance loading case. You can make similar calculations for two line outages. The effects of voltage drops, which increase series reactive losses (Equation 1.11) and reduce reactive power generation from transmission line capacitance, are not included in these calculations; these effects make the situation even worse.

Because of these nonlinear effects, voltage stability problems may develop over a period of only a few years.

### 2.5 Introduction to Voltage Stability Analysis: P-V Curves

The slower forms of voltage instability are often analyzed as steady-state problems; power flow simulation is the primary study method. "Snapshots" in time following an outage or during load buildup are simulated. Besides these post-disturbance power flows, two other power flow based methods are widely used: P-V curves and V-Q curves. These two methods determine steady-state loadability limits which are related to voltage stability. Conventional power flow programs can be used for approximate analysis.

P-V curves are useful for conceptual analysis of voltage stability and for study of radial systems. The method is also used for large meshed networks where P is the total load in an area and V is the voltage at a critical or representative bus. P can also be the power transfer across a transmission interface or interconnection. Voltage at several busses can be plotted. A disadvantage is that the power flow simulation will diverge near the nose or maximum power point on the curve. Another disadvantage is that generation must be realistically rescheduled as the area load is increased.

For conceptual analysis, P-V curves are convenient when load characteristics as a function of voltage are analyzed. For example a resistive load can be plotted with P_load = V²/R. The opposite extreme of a constant power (voltage independent) load is even simpler—it's a vertical line on the P-V curve. Section 2.7 describes these ideas further.

First, let's expand on impedance loads. A basic network theorem tells us that maximum power transmission occurs when the magnitude of the load impedance equals the magnitude of the source impedance. For higher load impedances (lower admittances), we are at high voltage, low current operating points. For higher admittances, we are at low voltage, high current operating points. Barbier and Barret provide the mathematical relations. For the simplest case of a resistance load and a reactance network, Figure 2-7 shows the relations of voltage, current, and power. As stated, maximum power occurs when the source and load impedance magnitudes are equal. We call the voltage at maximum power the critical voltage.

**Example 2-2**. For the simple thévenin system of Figure 2-7, find an expression for P = f(V). For unity power factor load, determine the maximum power and the voltage at maximum power (critical voltage). Normalize the variables based on the short circuit power, E²/X, with:

```
p_pu = P/(E²/X) and v_pu = V/E
```

Solution: The relations from Chapter 1 are rewritten in normalized form.

```
P = (EV/X) sin δ, p = v sin δ
Q = (E² - EV cos δ)/X, q = (1 - v cos δ)
```

Using the trigonometric identity v² sin² δ + v² cos² δ = v²:

```
p² = v² - v² cos² δ, or p = v√(1 - cos² δ)
```

At unity power factor, p = v√(1 - v²); taking the derivative and setting it equal to zero, we get the critical voltage and maximum power.

```
dp/dv = (1 - 2v²)/(2√(1 - v²)) = 0, 2v² = 1
```

```
V_crit = 1/√2 = 0.707 and P_max = √(1/2 - 1/4) = 0.5
```

Also, at maximum power, δ = sin⁻¹(P_max/V_crit) = 45°.

For the case of resistive load, we can verify that maximum power occurs when the load resistance R equals the source reactance X:

```
p = P_max × R/(X × R) = V_crit²/X = V²/R
```

**Example 2-3**. Repeat the previous problem with a purely reactive load. Calculate the "Voltage Collapse Proximity Indicator," (VCPI = dQ_s/dQ) where Q_s is generated or sending end reactive power and Q is load reactive power.

Solution: P = 0 and δ = 0. Therefore:

```
Q = (EV - V²)/X
dQ/dV = (E - 2V)/X = 0, V_crit = E/2
Q_max = (E²/2 - E²/4)/X = E²/(4X) = 0.25
```

We again confirmed the maximum power theorem. In normalized form:

```
V_crit = 0.5, Q_max = E²/(4X) = 0.25
```

We calculate the voltage collapse proximity indicator (VCPI) as follows:

```
Q_s = Q + (E² - EV)/X = Q + (1 - v)
dQ_s/dQ = 1 + dv/dQ = 1 - 1/(dQ/dv) = 1 - X/(E - 2V) = 1 - 1/(1 - 2v)
```

The voltage, V, goes from E at no load to E/2 at maximum load (Q_max): What about the VCPI? It goes from unity at no load to infinity at maximum load. Near maximum load, extremely large amounts of reactive power are required at the sending end to support an incremental increase in load. The VCPI is thus a very sensitive indicator of impending voltage collapse. The related quantities, reactive reserve activation and reactive losses, are also sensitive indicators.

For the elementary model, Figure 2-8 shows the family of normalized P-V curves for different power factors. At more leading power factors the maximum power is higher (leading power factor is obtained by shunt compensation). The critical voltage is also higher, which is a very important aspect of voltage stability.

### 2.6 Introduction to Voltage Stability Analysis: V-Q Curves

First, we can map the normalized p-v curves shown on Figure 2-8 onto v-q curves. For constant values of p, we note the q and v values (two pairs for each power factor), and then replot. Figure 2-9 shows the result. Again, the critical voltage is very high for high loadings (v is above 1 pu for p = 1 pu). The right side represents normal conditions where applying a capacitor bank raises voltage. The steep-sloped linear portions of the right side of the curves are equivalent to Figure 1-8 (rotate Figure 1-8 clockwise 90°).

For large systems, the curves are obtained by a series of power flow simulations. V-Q curves plot voltage at a test or critical bus versus reactive power on the same bus. A fictitious synchronous condenser is represented at the test bus. In computer program parlance, the bus is converted to a "PV bus" without reactive power limits. Power flow is simulated for a series of synchronous condenser voltage schedules, and the condenser reactive output is plotted versus scheduled voltage. Voltage is the independent variable and is the abscissa variable. Capacitive reactive power is plotted in the positive vertical direction. Without application of shunt reactive compensation at the test bus, the operating point is at the zero reactive point—corresponding to removal of the fictitious synchronous condenser. (These curves are often termed Q-V rather than a V-Q curves, but the V-Q terminology stresses that voltage rather than reactive power load is the independent variable. Q-V curves are produced by scheduling reactive load rather than voltage.)

V-Q curves have several advantages:

- Voltage security is closely related to reactive power, and a V-Q curve gives reactive power margin at the test bus. The reactive power margin is the MVAr distance from the operating point to either the bottom of the curve, or to a point where the voltage squared characteristic of an applied capacitor is tangent to the V-Q curve (Figure 2-10). The test bus could be representative of all busses in a "voltage control area" (an area where voltage magnitude changes are coherent).

- V-Q curves can be computed at points along a P-V curve to test system robustness.

- Characteristics of test bus shunt reactive compensation (capacitor, SVC, or synchronous condenser) can be plotted directly on the V-Q curve. The operating point is the intersection of the V-Q system characteristic and the reactive compensation characteristic (Figure 2-10b). This is useful since reactive compensation is often a solution to voltage stability problems.

- The slope of the V-Q curve indicates the stiffness of the test bus (the ΔV for a ΔQ).

- For more insight, the reactive power of generators can be plotted on the same graph. When nearby generators reach their VAr limits, the slope of the V-Q curve becomes less steep and the bottom of the curve is approached.

From a computation viewpoint, the artificial PV bus minimizes power flow divergence problems. Solutions can be obtained on the left side of the curve—divergence only occurs when voltages at busses away from the PV bus are dragged down. Generation rescheduling needs are minimal since the only changes in real power are caused by changes in losses. Starting values from the previous solution at a slightly different scheduled voltage are used so that each power flow solution is fast. The process can be automated so that the entire curve is computed at one time.

The effect of voltage sensitive loads, or of tap changing reaching limits, can be shown on V-Q curves. V-Q curves with voltage sensitive loads (i.e., prior to tap changing) will have much greater reactive power margins and much lower critical voltages. When tap changers hit limits, the curves tend to flatten out rather than turn up on the left side. These ideas are sketched on Figure 2-11.

V-Q curves are presently the workhorse method of voltage stability analysis at many utilities. Since the method artificially stresses a single bus, conclusions should be confirmed by more realistic methods.