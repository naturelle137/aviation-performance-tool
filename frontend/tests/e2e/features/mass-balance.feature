Feature: Standard Mass and Balance Calculation

  Scenario: Pilot performs a standard flight preparation
    # Maps to: CUJ 1
    # Relevant Requirements: [REQ-AC-01], [REQ-MB-01], [REQ-MB-02], [REQ-MB-07], [REQ-FE-02], [REQ-UQ-03]
    # Mitigated Hazards: [H-01], [H-05], [H-12]

    Given the user has loaded the aircraft profile for "D-EBPF" (REQ-AC-01)
    And the user is on the "Mass & Balance" calculation page
    When the user enters the following loading data:
      | Station          | Weight | Unit |
      | Pilot (Front L)  | 85     | kg   |
      | Co-Pilot (Front R)| 0      | kg   |
      | Fuel             | 120    | L    |
    And the user enters a "Taxi Fuel" of 5 Liters
    And the user enters a "Trip Fuel" of 45 Liters
    Then the system should display the "Takeoff Mass" as 986.4 kg (REQ-MB-01)
    And the system should display the "Landing Mass" as 954.0 kg (REQ-MB-07)
    And the "CG Envelope Chart" should be visible (REQ-MB-02)
    And the chart should show a green vector from "Takeoff CG" to "Landing CG" (REQ-MB-07)
    And no warnings should be displayed (REQ-MB-03)

  Scenario: Pilot exceeds MTOM limits
    # Maps to: CUJ 3
    # Relevant Requirements: [REQ-MB-04], [REQ-UI-10], [REQ-UQ-04]
    # Mitigated Hazards: [H-01], [H-05]

    Given the user acts as a pilot operating "D-EBPF" (MTOM: 1150 kg)
    When the user sets the "Rear Seat PAX" weight to 300 kg
    And the resulting "Total Mass" becomes 1250 kg
    Then the "Total Mass" display should immediately turn RED (REQ-UI-10)
    And a critical alert "Maximum Takeoff Mass Exceeded" should be visible (REQ-MB-04)
    And the "CG Envelope Chart" should show the current point outside the authorized envelope
    And the "Performance Calculation" button should be disabled or show a validation error
