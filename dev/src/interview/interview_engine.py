"""
Interview engine module.

Orchestrates the 5-phase interview process following the SOP framework.
"""

from typing import Dict, Any, Optional
from generators.template_engine import normalize_context


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
            
            # Validate phase 1
            if not self.validate_phase_results(phase1_data, phase_number=1):
                print("Warning: Phase 1 validation failed, using defaults")
                phase1_data = apply_phase_defaults(phase1_data, phase_number=1)
            
            self.context.update(phase1_data)
            
            # Phase 2: Technology Stack & Architecture
            phase2_data = self.run_phase(2)
            if phase2_data is None:
                return None
            
            # Validate phase 2 and cross-validate with phase 1
            if not self.validate_phase_results(phase2_data, phase_number=2):
                print("Warning: Phase 2 validation failed, using defaults")
                phase2_data = apply_phase_defaults(phase2_data, phase_number=2, previous_context=self.context)
            
            # Cross-phase validation
            phase2_data = cross_validate_phases(phase2_data, self.context)
            self.context.update(phase2_data)
            
            # Phase 3: Constraints & Requirements
            phase3_data = self.run_phase(3)
            if phase3_data is None:
                return None
            
            # Validate phase 3
            if not self.validate_phase_results(phase3_data, phase_number=3):
                print("Warning: Phase 3 validation failed, using defaults")
                phase3_data = apply_phase_defaults(phase3_data, phase_number=3, previous_context=self.context)
            
            self.context.update(phase3_data)
            
            # Phase 4: Development Workflow & Standards
            phase4_data = self.run_phase(4)
            if phase4_data is None:
                return None
            
            # Validate phase 4 and cross-validate with phase 1 (language)
            if not self.validate_phase_results(phase4_data, phase_number=4):
                print("Warning: Phase 4 validation failed, using defaults")
                phase4_data = apply_phase_defaults(phase4_data, phase_number=4, previous_context=self.context)
            
            # Cross-phase validation (coding standards based on language)
            phase4_data = cross_validate_phases(phase4_data, self.context)
            self.context.update(phase4_data)
            
            # Phase 5: Confirmation & Examples
            phase5_data = self.run_phase(5)
            if phase5_data is None:
                return None
            
            # Validate phase 5
            if not self.validate_phase_results(phase5_data, phase_number=5):
                print("Warning: Phase 5 validation failed, using defaults")
                phase5_data = apply_phase_defaults(phase5_data, phase_number=5, previous_context=self.context)
            
            self.context.update(phase5_data)
            
            # Final validation: ensure all required template variables are populated
            final_context = ensure_complete_context(self.context)
            
            # Show confirmation
            show_generation_preview(final_context)
            
            print("\n" + "=" * 60)
            print("Interview completed successfully!")
            print(f"Collected {len(final_context)} context variables.")
            
            return final_context
            
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
    
    def validate_phase_results(self, phase_data: Dict[str, Any], phase_number: int = 0) -> bool:
        """
        Validate that phase results contain required variables.
        
        Args:
            phase_data: Data from phase
            phase_number: Phase number for specific validation rules
            
        Returns:
            True if valid, False otherwise
        """
        if phase_data is None or len(phase_data) == 0:
            return False
        
        # Phase-specific validation
        if phase_number == 1:
            # Phase 1 requires: project_name, project_type, primary_language
            required = ['project_name', 'project_type', 'primary_language']
            return all(key in phase_data and phase_data[key] for key in required)
        
        elif phase_number == 2:
            # Phase 2: at least architecture should be set
            return 'architecture' in phase_data
        
        elif phase_number == 3:
            # Phase 3: deployment_type should be set
            return 'deployment_type' in phase_data
        
        elif phase_number == 4:
            # Phase 4: coding_standards and testing_framework should be set
            return 'coding_standards' in phase_data and 'testing_framework' in phase_data
        
        elif phase_number == 5:
            # Phase 5: confirmation should be set
            return 'confirmed' in phase_data
        
        # Basic validation
        return True
    
    def store_context(self, context: Dict[str, Any]):
        """
        Store context variables.
        
        Args:
            context: Context variables to store
        """
        self.context.update(context)


def apply_phase_defaults(phase_data: Dict[str, Any], phase_number: int, previous_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Apply default values for missing phase data.
    
    Args:
        phase_data: Phase data dictionary
        phase_number: Phase number
        previous_context: Context from previous phases
        
    Returns:
        Phase data with defaults applied
    """
    defaults = phase_data.copy() if phase_data else {}
    previous = previous_context or {}
    
    if phase_number == 1:
        defaults.setdefault('project_name', 'New Project')
        defaults.setdefault('project_type', 'spa')
        defaults.setdefault('primary_language', 'python')
    
    elif phase_number == 2:
        defaults.setdefault('technologies', [])
        defaults.setdefault('services', [])
        defaults.setdefault('ports', [])
        defaults.setdefault('architecture', previous.get('project_type', 'unknown'))
    
    elif phase_number == 3:
        defaults.setdefault('deployment_type', 'local')
        defaults.setdefault('networking', 'standard')
        defaults.setdefault('databases', [])
        defaults.setdefault('constraints', None)
    
    elif phase_number == 4:
        # Set defaults based on primary language
        primary_lang = previous.get('primary_language', 'python')
        if primary_lang == 'python':
            defaults.setdefault('coding_standards', 'PEP 8')
            defaults.setdefault('testing_framework', 'pytest')
        elif primary_lang in ['javascript', 'typescript']:
            defaults.setdefault('coding_standards', 'Standard')
            defaults.setdefault('testing_framework', 'jest')
        else:
            defaults.setdefault('coding_standards', 'Standard')
            defaults.setdefault('testing_framework', 'unknown')
        
        defaults.setdefault('file_organization', 'standard')
    
    elif phase_number == 5:
        defaults.setdefault('confirmed', True)
        defaults.setdefault('examples', None)
    
    return defaults


def cross_validate_phases(phase_data: Dict[str, Any], previous_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cross-validate phase data with previous phases.
    
    Args:
        phase_data: Current phase data
        previous_context: Context from previous phases
        
    Returns:
        Validated and adjusted phase data
    """
    validated = phase_data.copy()
    
    # If framework selected in phase 2, ensure related variables are set
    if 'frameworks' in validated and validated['frameworks']:
        framework = validated['frameworks'][0] if isinstance(validated['frameworks'], list) else validated['frameworks']
        
        # Set default ports based on framework
        if 'ports' not in validated or not validated['ports']:
            if framework == 'fastapi' or framework == 'django':
                validated['ports'] = [8000]
            elif framework == 'react' or framework == 'nextjs':
                validated['ports'] = [3000]
            elif framework == 'express':
                validated['ports'] = [3000]
    
    # If deployment type is docker/kubernetes, ensure containerization is set
    deployment_type = validated.get('deployment_type', '')
    if deployment_type == 'docker' and 'containerization' not in validated:
        validated['containerization'] = ['docker']
    elif deployment_type == 'kubernetes' and 'orchestration' not in validated:
        validated['orchestration'] = ['kubernetes']
    
    return validated


def ensure_complete_context(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure all required template variables are populated.
    
    Args:
        context: Context dictionary
        
    Returns:
        Complete context with all required variables
    """
    # Normalize context (this adds defaults)
    complete_context = normalize_context(context)
    
    # Required variables for template generation
    required_vars = [
        'project_name', 'project_type', 'primary_language',
        'technologies', 'architecture', 'deployment_type',
        'coding_standards', 'file_organization', 'testing_framework'
    ]
    
    # Ensure all required variables exist
    for var in required_vars:
        if var not in complete_context or complete_context[var] is None:
            # Use defaults from normalize_context
            pass
    
    return complete_context


def show_generation_preview(context: Dict[str, Any]):
    """
    Show preview of what will be generated.
    
    Args:
        context: Complete context dictionary
    """
    print("\n" + "=" * 60)
    print("Generation Preview")
    print("=" * 60)
    print(f"Project: {context.get('project_name', 'Unknown')}")
    print(f"Type: {context.get('project_type', 'Unknown')}")
    print(f"Language: {context.get('primary_language', 'Unknown')}")
    print(f"Technologies: {context.get('technologies', 'Unknown')}")
    print(f"Architecture: {context.get('architecture', 'Unknown')}")
    print(f"Deployment: {context.get('deployment_type', 'Unknown')}")
    print(f"Coding Standards: {context.get('coding_standards', 'Unknown')}")
    print(f"Testing: {context.get('testing_framework', 'Unknown')}")
    print("=" * 60)
    print("\nThe following files will be generated:")
    print("  - .cursorrules")
    print("  - .cursor/rules/ (with rule content files)")
    print("  - .cursor/commands/ (with command files)")
    print("  - .cursor/AGENTS.md")
    print("  - source_list.json")
    print("=" * 60)

