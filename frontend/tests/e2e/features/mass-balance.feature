Feature: Mass and Balance Calculation
  As a pilot
  I want to calculate the mass and balance of my aircraft
  So that I can verify the flight is within CG limits

  Background:
    Given I have an aircraft "D-EABC" with weight stations configured
    And the aircraft has a normal CG envelope defined

  @critical
  Scenario: Calculate M&B for a normal flight
    Given I am on the calculation page
    When I select aircraft "D-EABC"
    And I enter the following weights:
      | Station       | Weight (kg) |
      | Pilot         | 85          |
      | Copilot       | 75          |
      | Rear Passengers | 0         |
      | Baggage       | 20          |
    And I enter fuel quantity "100" liters
    And I enter trip fuel "40" liters
    And I click "Calculate M&B"
    Then I should see the M&B results
    And the takeoff weight should be displayed
    And the landing weight should be displayed
    And I should see the M&B chart
    And the takeoff CG should be within limits
    And the landing CG should be within limits

  @critical
  Scenario: Warning when weight exceeds MTOW
    Given I am on the calculation page
    When I select aircraft "D-EABC"
    And I enter weights that would exceed MTOW
    And I click "Calculate M&B"
    Then I should see a weight warning
    And the warning should mention "exceeds MTOW"

  Scenario: Warning when CG is out of limits
    Given I am on the calculation page
    When I select aircraft "D-EABC"
    And I enter weights that cause the CG to be out of limits
    And I click "Calculate M&B"
    Then I should see a CG warning
    And the chart should highlight the out-of-limits point

  Scenario: Calculate with only pilot
    Given I am on the calculation page
    When I select aircraft "D-EABC"
    And I enter only pilot weight of 85 kg
    And I enter fuel quantity "50" liters
    And I click "Calculate M&B"
    Then the calculation should succeed
    And the payload should show 85 kg
