"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

import json
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import force_str

def validate_challenge_import_json(json_data):
    """
    Validates the challenge import JSON data format and required fields.
    
    Args:
        json_data: The parsed JSON data to validate
        
    Returns:
        tuple: (is_valid, results)
        - is_valid: Boolean indicating if validation passed
        - results: Dictionary with validated data and error information
            {
                'success': bool,
                'challenges_total': int,
                'challenges_valid': int,
                'challenges_invalid': int,
                'errors': list of validation error dicts,
                'valid_challenges': list of valid challenge dicts
            }
    """
    results = {
        'success': False,
        'challenges_total': 0,
        'challenges_valid': 0,
        'challenges_invalid': 0,
        'errors': [],
        'valid_challenges': []
    }
    
    # Check if JSON has a challenges array
    if not isinstance(json_data, dict) or 'challenges' not in json_data:
        results['errors'].append({
            'type': 'format',
            'message': force_str(_('Invalid JSON format: Root must be an object with a "challenges" array'))
        })
        return False, results
    
    challenges = json_data.get('challenges', [])
    
    # Ensure challenges is a list
    if not isinstance(challenges, list):
        results['errors'].append({
            'type': 'format',
            'message': force_str(_('Invalid JSON format: "challenges" must be an array'))
        })
        return False, results
    
    results['challenges_total'] = len(challenges)
    
    # If no challenges found
    if len(challenges) == 0:
        results['errors'].append({
            'type': 'content',
            'message': force_str(_('No challenges found in the import file'))
        })
        return False, results
    
    # Validate each challenge
    for i, challenge in enumerate(challenges):
        challenge_errors = []
        
        # Required fields validation
        required_fields = ['name', 'description', 'category', 'difficulty', 'value']
        for field in required_fields:
            if field not in challenge:
                challenge_errors.append({
                    'field': field,
                    'message': force_str(_(f'Missing required field: {field}'))
                })
        
        # Data type validation
        if 'name' in challenge and not isinstance(challenge['name'], str):
            challenge_errors.append({
                'field': 'name',
                'message': force_str(_('Challenge name must be a string'))
            })
            
        if 'description' in challenge and not isinstance(challenge['description'], str):
            challenge_errors.append({
                'field': 'description',
                'message': force_str(_('Challenge description must be a string'))
            })
            
        if 'category' in challenge and not isinstance(challenge['category'], str):
            challenge_errors.append({
                'field': 'category',
                'message': force_str(_('Category must be a string'))
            })
            
        if 'difficulty' in challenge:
            if not isinstance(challenge['difficulty'], int) or challenge['difficulty'] < 1 or challenge['difficulty'] > 5:
                challenge_errors.append({
                    'field': 'difficulty',
                    'message': force_str(_('Difficulty must be an integer between 1 and 5'))
                })
                
        if 'value' in challenge:
            if not isinstance(challenge['value'], int) or challenge['value'] <= 0:
                # Check if points is provided as a fallback
                if 'points' in challenge and isinstance(challenge['points'], int) and challenge['points'] > 0:
                    challenge['value'] = challenge['points']
                else:
                    challenge_errors.append({
                        'field': 'value',
                        'message': force_str(_('Value must be a positive integer'))
                    })
        
        # Validate flags
        if 'flags' in challenge:
            if not isinstance(challenge['flags'], list):
                challenge_errors.append({
                    'field': 'flags',
                    'message': force_str(_('Flags must be an array'))
                })
            else:
                for j, flag in enumerate(challenge['flags']):
                    if not isinstance(flag, dict):
                        challenge_errors.append({
                            'field': f'flags[{j}]',
                            'message': force_str(_('Flag must be an object'))
                        })
                    elif 'flag' not in flag:
                        challenge_errors.append({
                            'field': f'flags[{j}]',
                            'message': force_str(_('Flag object must contain a "flag" field'))
                        })
                    elif not isinstance(flag['flag'], str):
                        challenge_errors.append({
                            'field': f'flags[{j}].flag',
                            'message': force_str(_('Flag value must be a string'))
                        })
        elif 'flag' in challenge and isinstance(challenge['flag'], str):
            # Support legacy single flag format
            challenge['flags'] = [{"flag": challenge['flag'], "type": "static"}]
        else:
            challenge_errors.append({
                'field': 'flags',
                'message': force_str(_('Challenge must have at least one flag'))
            })
        
        # Validate hints if present
        if 'hints' in challenge and isinstance(challenge['hints'], list):
            for j, hint in enumerate(challenge['hints']):
                if isinstance(hint, str):
                    # Convert to expected format
                    challenge['hints'][j] = {"content": hint, "cost": 0}
                elif isinstance(hint, dict):
                    if 'content' not in hint:
                        challenge_errors.append({
                            'field': f'hints[{j}]',
                            'message': force_str(_('Hint object must contain a "content" field'))
                        })
                    elif not isinstance(hint['content'], str):
                        challenge_errors.append({
                            'field': f'hints[{j}].content',
                            'message': force_str(_('Hint content must be a string'))
                        })
                    
                    if 'cost' in hint and (not isinstance(hint['cost'], int) or hint['cost'] < 0):
                        challenge_errors.append({
                            'field': f'hints[{j}].cost',
                            'message': force_str(_('Hint cost must be a non-negative integer'))
                        })
                else:
                    challenge_errors.append({
                        'field': f'hints[{j}]',
                        'message': force_str(_('Hint must be a string or an object'))
                    })
        
        # Store validation results
        if challenge_errors:
            challenge_name = challenge.get('name', f'Challenge #{i+1}')
            results['challenges_invalid'] += 1
            results['errors'].append({
                'challenge': challenge_name,
                'index': i,
                'errors': challenge_errors
            })
        else:
            results['challenges_valid'] += 1
            results['valid_challenges'].append(challenge)
    
    # Determine overall success
    results['success'] = results['challenges_valid'] > 0 and results['challenges_invalid'] == 0
    
    return results['success'], results
