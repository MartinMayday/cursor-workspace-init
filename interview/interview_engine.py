"""
Interview engine module.

Orchestrates the 5-phase interview process following the SOP framework.
"""

from typing import Dict, Any, Optional


class InterviewEngine:
    """Engine for conducting 5-phase interview."""
    
    def __init__(self):
        """Initialize interview engine."""
        self.context: Dict[str, Any] = {}
        self.current_phase = 0
    
    def conduct_interview(self) -> Optional[Dict[str, Any]]:
        """
        Conduct the complete 5-phase interview.
        
        Returns:
            Dictionary containing extracted context variables, or None if cancelled
        """
        print("Starting 5-phase interview for new project setup...")
        print("=" * 60)
        
        try:
            # Phase 1: Project Classification
            phase1_data = self.run_phase(1)
            if phase1_data is None:
                return None
            self.context.update(phase1_data)
            
            # Phase 2: Technology Stack & Architecture
            phase2_data = self.run_phase(2)
            if phase2_data is None:
                return None
            self.context.update(phase2_data)
            
            # Phase 3: Constraints & Requirements
            phase3_data = self.run_phase(3)
            if phase3_data is None:
                return None
            self.context.update(phase3_data)
            
            # Phase 4: Development Workflow & Standards
            phase4_data = self.run_phase(4)
            if phase4_data is None:
                return None
            self.context.update(phase4_data)
            
            # Phase 5: Confirmation & Examples
            phase5_data = self.run_phase(5)
            if phase5_data is None:
                return None
            self.context.update(phase5_data)
            
            print("\n" + "=" * 60)
            print("Interview completed successfully!")
            print(f"Collected {len(self.context)} context variables.")
            
            return self.context
            
        except KeyboardInterrupt:
            print("\n\nInterview cancelled by user.")
            return None
        except Exception as e:
            print(f"\nError during interview: {e}")
            return None
    
    def run_phase(self, phase_number: int) -> Optional[Dict[str, Any]]:
        """
        Run a specific interview phase.
        
        Args:
            phase_number: Phase number (1-5)
            
        Returns:
            Dictionary containing phase data, or None if cancelled
        """
        self.current_phase = phase_number
        
        if phase_number == 1:
            from interview.phase1_classification import run_phase1
            return run_phase1()
        elif phase_number == 2:
            from interview.phase2_tech_stack import run_phase2
            return run_phase2(self.context)
        elif phase_number == 3:
            from interview.phase3_constraints import run_phase3
            return run_phase3(self.context)
        elif phase_number == 4:
            from interview.phase4_workflow import run_phase4
            return run_phase4(self.context)
        elif phase_number == 5:
            from interview.phase5_confirmation import run_phase5
            return run_phase5(self.context)
        else:
            raise ValueError(f"Invalid phase number: {phase_number}")
    
    def validate_phase_results(self, phase_data: Dict[str, Any]) -> bool:
        """
        Validate that phase results contain required variables.
        
        Args:
            phase_data: Data from phase
            
        Returns:
            True if valid, False otherwise
        """
        # Basic validation - can be expanded per phase
        return phase_data is not None and len(phase_data) > 0
    
    def store_context(self, context: Dict[str, Any]):
        """
        Store context variables.
        
        Args:
            context: Context variables to store
        """
        self.context.update(context)

