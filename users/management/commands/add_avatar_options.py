"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.core.files import File
from users.avatar_models import AvatarCategory, AvatarOption
import os
import tempfile
import xml.etree.ElementTree as ET
import random
import math

class Command(BaseCommand):
    help = 'Adds additional avatar options to existing categories'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count', 
            type=int, 
            default=5,
            help='Number of avatars to create per category'
        )

    def handle(self, *args, **options):
        count = options.get('count', 5)
        
        # Get all categories
        categories = AvatarCategory.objects.all()
        if not categories.exists():
            self.stdout.write(self.style.ERROR('No categories found. Run create_default_avatars first.'))
            return
            
        for category in categories:
            self.stdout.write(f'Adding avatars to category: {category.name}')
            
            # Check how many avatars already exist in this category
            existing_count = category.avatars.count()
            self.stdout.write(f'  - Found {existing_count} existing avatars')
            
            # Create additional avatars
            new_count = 0
            for i in range(existing_count, existing_count + count):
                avatar_name = f"{category.name} {i+1}"
                
                # Skip if this avatar already exists
                if category.avatars.filter(name=avatar_name).exists():
                    continue
                    
                # Create SVG based on category
                svg_content = self._generate_svg_for_category(category)
                
                # Save the SVG to a temporary file
                with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as temp_file:
                    temp_file.write(svg_content.encode('utf-8'))
                    temp_file_path = temp_file.name
                
                try:
                    # Create the avatar option
                    with open(temp_file_path, 'rb') as f:
                        avatar = AvatarOption(
                            name=avatar_name,
                            category=category,
                            is_default=(existing_count + new_count == 0),  # First one is default
                            display_order=i
                        )
                        file_name = f"{slugify(avatar_name)}.svg"
                        avatar.image.save(file_name, File(f), save=True)
                    
                    new_count += 1
                    self.stdout.write(self.style.SUCCESS(f'  - Created avatar: {avatar_name}'))
                finally:
                    # Clean up the temporary file
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
            
            self.stdout.write(self.style.SUCCESS(f'Added {new_count} new avatars to {category.name}'))
        
        self.stdout.write(self.style.SUCCESS('Avatar generation complete'))

    def _generate_svg_for_category(self, category):
        """Generate a unique SVG based on the category"""
        
        # SVG base
        svg = ET.Element('svg', {
            'xmlns': 'http://www.w3.org/2000/svg',
            'width': '512',
            'height': '512',
            'viewBox': '0 0 512 512'
        })
        
        # Background
        ET.SubElement(svg, 'rect', {
            'width': '512',
            'height': '512',
            'fill': self._get_background_color(category)
        })
        
        # Add category-specific elements
        if category.slug == 'tech':
            self._add_tech_elements(svg)
        elif category.slug == 'animals':
            self._add_animal_elements(svg)
        elif category.slug == 'geometric':
            self._add_geometric_elements(svg)
        elif category.slug == 'gaming':
            self._add_gaming_elements(svg)
        elif category.slug == 'space':
            self._add_space_elements(svg)
        elif category.slug == 'abstract':
            self._add_abstract_elements(svg)
        else:
            # Default design for any other category
            self._add_abstract_elements(svg)
        
        # Convert to string
        return ET.tostring(svg, encoding='unicode')

    def _get_background_color(self, category):
        """Get a suitable background color for the category"""
        colors = {
            'tech': ['#3498db', '#2980b9', '#34495e', '#2c3e50', '#1abc9c', '#16a085'],
            'animals': ['#f1c40f', '#f39c12', '#e67e22', '#d35400', '#27ae60', '#2ecc71'],
            'geometric': ['#9b59b6', '#8e44ad', '#3498db', '#2980b9', '#1abc9c', '#16a085'],
            'gaming': ['#e74c3c', '#c0392b', '#9b59b6', '#8e44ad', '#2c3e50', '#34495e'],
            'space': ['#2c3e50', '#34495e', '#8e44ad', '#9b59b6', '#2980b9', '#3498db'],
            'abstract': ['#1abc9c', '#16a085', '#e74c3c', '#c0392b', '#f39c12', '#f1c40f']
        }
        
        category_colors = colors.get(category.slug, colors['abstract'])
        return random.choice(category_colors)

    def _add_tech_elements(self, svg):
        """Add technology-themed elements to SVG"""
        # Circuit-like pattern
        g = ET.SubElement(svg, 'g', {'fill': 'none', 'stroke': '#ffffff', 'stroke-width': '4'})
        
        # Random circuit lines
        for _ in range(10):
            x1 = random.randint(50, 462)
            y1 = random.randint(50, 462)
            x2 = x1 + random.choice([-1, 1]) * random.randint(50, 150)
            y2 = y1 + random.choice([-1, 1]) * random.randint(50, 150)
            
            ET.SubElement(g, 'line', {
                'x1': str(x1),
                'y1': str(y1),
                'x2': str(x2),
                'y2': str(y2)
            })
        
        # Add some circles for nodes
        for _ in range(8):
            cx = random.randint(80, 432)
            cy = random.randint(80, 432)
            r = random.randint(5, 15)
            
            ET.SubElement(svg, 'circle', {
                'cx': str(cx),
                'cy': str(cy),
                'r': str(r),
                'fill': '#ffffff'
            })

    def _add_animal_elements(self, svg):
        """Add animal-themed elements to SVG"""
        # Simple animal face
        # Head
        ET.SubElement(svg, 'circle', {
            'cx': '256',
            'cy': '256',
            'r': '120',
            'fill': '#ffffff'
        })
        
        # Eyes
        eye_colors = ['#2c3e50', '#34495e', '#7f8c8d', '#95a5a6']
        eye_color = random.choice(eye_colors)
        
        ET.SubElement(svg, 'circle', {
            'cx': '206',
            'cy': '226',
            'r': '25',
            'fill': eye_color
        })
        
        ET.SubElement(svg, 'circle', {
            'cx': '306',
            'cy': '226',
            'r': '25',
            'fill': eye_color
        })
        
        # Random features (ears, nose, etc.)
        if random.random() > 0.5:  # 50% chance for ears
            # Left ear
            ET.SubElement(svg, 'path', {
                'd': 'M 180 180 L 140 120 L 200 150 Z',
                'fill': '#ffffff'
            })
            
            # Right ear
            ET.SubElement(svg, 'path', {
                'd': 'M 332 180 L 372 120 L 312 150 Z',
                'fill': '#ffffff'
            })
        
        # Nose
        nose_shapes = [
            'M 256 276 L 236 296 L 276 296 Z',  # Triangle
            'M 236 286 C 236 306, 276 306, 276 286 Z'  # Rounded
        ]
        
        ET.SubElement(svg, 'path', {
            'd': random.choice(nose_shapes),
            'fill': random.choice(['#e74c3c', '#c0392b', '#2c3e50', '#34495e'])
        })

    def _add_geometric_elements(self, svg):
        """Add geometric elements to SVG"""
        # Add several random geometric shapes
        shapes = []
        
        # Generate between 3-8 shapes
        for _ in range(random.randint(3, 8)):
            shape_type = random.choice(['circle', 'rect', 'polygon'])
            
            if shape_type == 'circle':
                shapes.append(ET.SubElement(svg, 'circle', {
                    'cx': str(random.randint(100, 412)),
                    'cy': str(random.randint(100, 412)),
                    'r': str(random.randint(30, 80)),
                    'fill': self._get_random_color(opacity=0.7)
                }))
            
            elif shape_type == 'rect':
                width = random.randint(50, 150)
                height = random.randint(50, 150)
                shapes.append(ET.SubElement(svg, 'rect', {
                    'x': str(random.randint(50, 512 - width - 50)),
                    'y': str(random.randint(50, 512 - height - 50)),
                    'width': str(width),
                    'height': str(height),
                    'fill': self._get_random_color(opacity=0.7)
                }))
            
            elif shape_type == 'polygon':
                # Create a random polygon with 3-6 points
                points = []
                for i in range(random.randint(3, 6)):
                    angle = i * (2 * math.pi / random.randint(3, 6))
                    radius = random.randint(50, 150)
                    x = 256 + radius * math.cos(angle)
                    y = 256 + radius * math.sin(angle)
                    points.append(f"{x},{y}")
                
                shapes.append(ET.SubElement(svg, 'polygon', {
                    'points': ' '.join(points),
                    'fill': self._get_random_color(opacity=0.7)
                }))

    def _add_gaming_elements(self, svg):
        """Add gaming-themed elements to SVG"""
        # Draw a simple game controller or pixel art
        if random.random() > 0.5:  # Controller
            # Controller body
            ET.SubElement(svg, 'rect', {
                'x': '156',
                'y': '206',
                'width': '200',
                'height': '100',
                'rx': '20',
                'fill': '#ffffff'
            })
            
            # Left thumbstick
            ET.SubElement(svg, 'circle', {
                'cx': '186',
                'cy': '236',
                'r': '20',
                'fill': '#34495e'
            })
            
            # Right thumbstick
            ET.SubElement(svg, 'circle', {
                'cx': '326',
                'cy': '236',
                'r': '20',
                'fill': '#34495e'
            })
            
            # Buttons
            button_colors = ['#e74c3c', '#2ecc71', '#3498db', '#f1c40f']
            random.shuffle(button_colors)
            
            ET.SubElement(svg, 'circle', {
                'cx': '286',
                'cy': '236',
                'r': '10',
                'fill': button_colors[0]
            })
            
            ET.SubElement(svg, 'circle', {
                'cx': '306',
                'cy': '216',
                'r': '10',
                'fill': button_colors[1]
            })
            
            ET.SubElement(svg, 'circle', {
                'cx': '306',
                'cy': '256',
                'r': '10',
                'fill': button_colors[2]
            })
            
            ET.SubElement(svg, 'circle', {
                'cx': '326',
                'cy': '236',
                'r': '10',
                'fill': button_colors[3]
            })
        
        else:  # Pixel character
            # Create a grid of rectangles for a pixelated character
            pixel_size = 20
            pixel_colors = ['#ffffff', '#e74c3c', '#3498db', '#f1c40f', '#2ecc71']
            
            # Simple pixel art character (8x8 grid centered)
            start_x = 256 - (4 * pixel_size)
            start_y = 256 - (4 * pixel_size)
            
            # Create a simple pattern
            for y in range(8):
                for x in range(8):
                    if random.random() > 0.5:  # 50% chance to draw a pixel
                        ET.SubElement(svg, 'rect', {
                            'x': str(start_x + (x * pixel_size)),
                            'y': str(start_y + (y * pixel_size)),
                            'width': str(pixel_size),
                            'height': str(pixel_size),
                            'fill': random.choice(pixel_colors)
                        })

    def _add_space_elements(self, svg):
        """Add space-themed elements to SVG"""
        # Add stars
        for _ in range(50):
            x = random.randint(10, 502)
            y = random.randint(10, 502)
            r = random.randint(1, 3)
            
            ET.SubElement(svg, 'circle', {
                'cx': str(x),
                'cy': str(y),
                'r': str(r),
                'fill': '#ffffff'
            })
        
        # Add a planet
        planet_cx = random.randint(150, 362)
        planet_cy = random.randint(150, 362)
        planet_r = random.randint(60, 100)
        
        planet = ET.SubElement(svg, 'circle', {
            'cx': str(planet_cx),
            'cy': str(planet_cy),
            'r': str(planet_r),
            'fill': self._get_random_color()
        })
        
        # Add ring to some planets
        if random.random() > 0.5:
            ET.SubElement(svg, 'ellipse', {
                'cx': str(planet_cx),
                'cy': str(planet_cy),
                'rx': str(planet_r + 20),
                'ry': str(planet_r / 3),
                'fill': 'none',
                'stroke': '#ffffff',
                'stroke-width': '4'
            })

    def _add_abstract_elements(self, svg):
        """Add abstract artistic elements to SVG"""
        # Choose a random abstract style
        style = random.choice(['waves', 'circles', 'lines', 'gradient'])
        
        if style == 'waves':
            # Create wavy patterns
            for i in range(5):
                path_data = 'M 0 ' + str(100 + i * 80)
                
                for x in range(0, 512, 20):
                    y_offset = random.randint(-20, 20)
                    path_data += ' L ' + str(x) + ' ' + str(100 + i * 80 + y_offset)
                
                ET.SubElement(svg, 'path', {
                    'd': path_data,
                    'stroke': '#ffffff',
                    'stroke-width': '3',
                    'fill': 'none',
                    'opacity': '0.7'
                })
        
        elif style == 'circles':
            # Create concentric or scattered circles
            if random.random() > 0.5:  # Concentric
                for i in range(10):
                    ET.SubElement(svg, 'circle', {
                        'cx': '256',
                        'cy': '256',
                        'r': str(250 - i * 25),
                        'fill': 'none',
                        'stroke': self._get_random_color(),
                        'stroke-width': '2',
                        'opacity': str(0.3 + i * 0.07)
                    })
            else:  # Scattered
                for _ in range(15):
                    ET.SubElement(svg, 'circle', {
                        'cx': str(random.randint(50, 462)),
                        'cy': str(random.randint(50, 462)),
                        'r': str(random.randint(10, 60)),
                        'fill': self._get_random_color(opacity=0.6)
                    })
        
        elif style == 'lines':
            # Create a pattern of intersecting lines
            g = ET.SubElement(svg, 'g', {
                'stroke': '#ffffff',
                'stroke-width': '2',
                'opacity': '0.7'
            })
            
            for _ in range(20):
                x1 = random.randint(0, 512)
                y1 = random.randint(0, 512)
                x2 = random.randint(0, 512)
                y2 = random.randint(0, 512)
                
                ET.SubElement(g, 'line', {
                    'x1': str(x1),
                    'y1': str(y1),
                    'x2': str(x2),
                    'y2': str(y2)
                })
        
        elif style == 'gradient':
            # Create abstract gradient shapes
            for _ in range(5):
                x = random.randint(50, 462)
                y = random.randint(50, 462)
                rx = random.randint(50, 150)
                ry = random.randint(50, 150)
                
                # Use a radial gradient
                gradient_id = f"gradient-{random.randint(1000, 9999)}"
                
                # Create a radial gradient definition
                radialGradient = ET.SubElement(svg, 'radialGradient', {
                    'id': gradient_id,
                    'cx': '0.5',
                    'cy': '0.5',
                    'r': '0.5',
                    'fx': '0.5',
                    'fy': '0.5'
                })
                
                ET.SubElement(radialGradient, 'stop', {
                    'offset': '0%',
                    'stop-color': self._get_random_color(),
                    'stop-opacity': '1'
                })
                
                ET.SubElement(radialGradient, 'stop', {
                    'offset': '100%',
                    'stop-color': self._get_random_color(),
                    'stop-opacity': '0'
                })
                
                # Create an ellipse with the gradient
                ET.SubElement(svg, 'ellipse', {
                    'cx': str(x),
                    'cy': str(y),
                    'rx': str(rx),
                    'ry': str(ry),
                    'fill': f"url(#{gradient_id})"
                })

    def _get_random_color(self, opacity=1.0):
        """Generate a random color with optional opacity"""
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        
        if opacity < 1.0:
            return f"rgba({r}, {g}, {b}, {opacity})"
        else:
            return f"#{r:02x}{g:02x}{b:02x}"
