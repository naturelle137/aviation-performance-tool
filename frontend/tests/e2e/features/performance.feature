Feature: Performance Calculation in High Density Altitude

  Scenario: Pilot plans takeoff at high altitude and temperature
    # Maps to: CUJ 2
    # Relevant Requirements: [REQ-PF-05], [REQ-PF-13], [REQ-PF-14], [REQ-PF-15]
    # Mitigated Hazards: [H-06], [H-11], [H-13]

    Given the user has selected airport "LFLJ" (Courchevel) with elevation 6588 ft
    And the user enters the following environmental conditions:
      | Parameter   | Value | Unit |
      | Temperature | 30    | °C   |
      | QNH         | 1013  | hPa  |
    When the user navigates to the "Performance" tab
    Then the system should display a "High Density Altitude" warning (REQ-PF-05)
    And the system should identify the conditions as "Outside POH Standard Range"
    And the system should apply the "Extrapolation Penalty" of 20% (REQ-PF-14)
    And the user should see a mandatory confirmation dialog: "Pilot-in-Command acknowledges extrapolated data" (REQ-PF-15)
    When the user confirms the dialog
    Then the "Takeoff Distance Required" should be calculated using the penalised formula (REQ-PF-13)
