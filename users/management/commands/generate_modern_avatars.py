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
import colorsys

class Command(BaseCommand):
    help = 'Generates modern, professional avatars for the platform'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count', 
            type=int, 
            default=10,
            help='Number of avatars to create per category'
        )
        parser.add_argument(
            '--recreate',
            action='store_true',
            help='Recreate all avatar categories and options (warning: this will delete existing ones)',
        )

    def handle(self, *args, **options):
        count = options.get('count', 10)
        recreate = options.get('recreate', False)
        
        if recreate:
            self.stdout.write(self.style.WARNING('Recreating all avatar categories and options...'))
            AvatarOption.objects.all().delete()
            AvatarCategory.objects.all().delete()
        
        # Create modern categories
        categories = [
            {
                'name': 'Abstract',
                'slug': 'abstract',
                'description': 'Creative abstract designs',
                'display_order': 1,
            },
            {
                'name': 'Tech',
                'slug': 'tech',
                'description': 'Technology themed avatars',
                'display_order': 2,
            },
            {
                'name': 'Cybersecurity',
                'slug': 'cybersecurity',
                'description': 'Security-themed avatars',
                'display_order': 3,
            },
            {
                'name': 'Minimal',
                'slug': 'minimal',
                'description': 'Clean minimal designs',
                'display_order': 4,
            },
            {
                'name': 'Gradient',
                'slug': 'gradient',
                'description': 'Smooth gradient designs',
                'display_order': 5,
            }
        ]
        
        # Create each category
        for cat_data in categories:
            category, created = AvatarCategory.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Category already exists: {category.name}'))
            
            # Generate avatars for this category
            existing_count = category.avatars.count()
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
                            is_default=(existing_count + new_count == 0 and category.slug == 'geometric'),
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
        
        self.stdout.write(self.style.SUCCESS('Modern avatar generation complete'))

    def _generate_svg_for_category(self, category):
        """Generate a unique SVG based on the category"""
        
        # SVG base
        svg = ET.Element('svg', {
            'xmlns': 'http://www.w3.org/2000/svg',
            'width': '512',
            'height': '512',
            'viewBox': '0 0 512 512'
        })
        
        if category.slug == 'abstract':
            self._generate_abstract_avatar(svg)
        elif category.slug == 'tech':
            self._generate_tech_avatar(svg)
        elif category.slug == 'cybersecurity':
            self._generate_cybersecurity_avatar(svg)
        elif category.slug == 'minimal':
            self._generate_minimal_avatar(svg)
        elif category.slug == 'gradient':
            self._generate_gradient_avatar(svg)
        else:
            # Default to abstract design
            self._generate_abstract_avatar(svg)
        
        # Convert to string
        return ET.tostring(svg, encoding='unicode')

    def _generate_geometric_avatar(self, svg):
        """Generate a clean geometric avatar design"""
        # Choose a base color 
        hue = random.random()
        base_color = self._hsl_to_hex(hue, 0.6, 0.6)
        accent_color = self._hsl_to_hex((hue + 0.5) % 1.0, 0.7, 0.5)
        
        # Background
        ET.SubElement(svg, 'rect', {
            'width': '512',
            'height': '512',
            'fill': base_color
        })
        
        # Choose a random pattern type
        pattern_type = random.choice(['triangles', 'squares', 'circles', 'hexagons'])
        
        if pattern_type == 'triangles':
            # Create triangular pattern
            for _ in range(3):
                size = random.randint(100, 300)
                x = random.randint(0, 512 - size)
                y = random.randint(0, 512 - size)
                
                points = []
                if random.random() > 0.5:
                    # Right triangle
                    points = f"{x},{y} {x+size},{y} {x},{y+size}"
                else:
                    # Equilateral triangle
                    height = size * 0.866  # sqrt(3)/2
                    points = f"{x},{y+height} {x+size/2},{y} {x+size},{y+height}"
                
                ET.SubElement(svg, 'polygon', {
                    'points': points,
                    'fill': accent_color,
                    'opacity': str(random.uniform(0.5, 0.9))
                })
            
        elif pattern_type == 'squares':
            # Create square/rectangle pattern
            for _ in range(4):
                width = random.randint(80, 250)
                height = random.randint(80, 250)
                x = random.randint(0, 512 - width)
                y = random.randint(0, 512 - height)
                
                ET.SubElement(svg, 'rect', {
                    'x': str(x),
                    'y': str(y),
                    'width': str(width),
                    'height': str(height),
                    'fill': accent_color,
                    'opacity': str(random.uniform(0.5, 0.9))
                })
                
        elif pattern_type == 'circles':
            # Create circle pattern
            for _ in range(5):
                radius = random.randint(40, 150)
                cx = random.randint(radius, 512 - radius)
                cy = random.randint(radius, 512 - radius)
                
                ET.SubElement(svg, 'circle', {
                    'cx': str(cx),
                    'cy': str(cy),
                    'r': str(radius),
                    'fill': accent_color,
                    'opacity': str(random.uniform(0.5, 0.9))
                })
                
        elif pattern_type == 'hexagons':
            # Create hexagon pattern
            for _ in range(3):
                size = random.randint(80, 200)
                x = random.randint(size, 512 - size)
                y = random.randint(size, 512 - size)
                
                # Create hexagon points
                points = []
                for i in range(6):
                    angle = i * 60 * (math.pi / 180)
                    px = x + size * math.cos(angle)
                    py = y + size * math.sin(angle)
                    points.append(f"{px},{py}")
                
                ET.SubElement(svg, 'polygon', {
                    'points': ' '.join(points),
                    'fill': accent_color,
                    'opacity': str(random.uniform(0.5, 0.9))
                })
    
    def _generate_abstract_avatar(self, svg):
        """Generate an abstract artistic avatar"""
        # Use a vibrant color palette
        colors = [
            self._hsl_to_hex(random.random(), 0.7, 0.6),
            self._hsl_to_hex(random.random(), 0.8, 0.5),
            self._hsl_to_hex(random.random(), 0.6, 0.7)
        ]
        
        # Background
        ET.SubElement(svg, 'rect', {
            'width': '512',
            'height': '512',
            'fill': colors[0]
        })
        
        # Create abstract shapes
        shape_type = random.choice(['blobs', 'waves', 'curves'])
        
        if shape_type == 'blobs':
            # Create organic blob shapes
            for i in range(2):
                # Create a blob using bezier curves
                path_data = 'M 256,256 '
                
                # Add random control points
                for j in range(random.randint(4, 8)):
                    angle = j * (2 * math.pi / random.randint(4, 8))
                    radius = random.randint(100, 200)
                    
                    x1 = 256 + radius * 0.8 * math.cos(angle)
                    y1 = 256 + radius * 0.8 * math.sin(angle)
                    x2 = 256 + radius * 0.8 * math.cos(angle + 0.5)
                    y2 = 256 + radius * 0.8 * math.sin(angle + 0.5)
                    x = 256 + radius * math.cos(angle + 1)
                    y = 256 + radius * math.sin(angle + 1)
                    
                    path_data += f'C {x1},{y1} {x2},{y2} {x},{y} '
                
                path_data += 'Z'
                
                ET.SubElement(svg, 'path', {
                    'd': path_data,
                    'fill': colors[i+1],
                    'opacity': str(random.uniform(0.6, 0.9))
                })
                
        elif shape_type == 'waves':
            # Create wave patterns
            for i in range(2):
                # Create a wavy pattern
                amplitude = random.randint(40, 80)
                frequency = random.randint(1, 3)
                path_data = 'M 0,256 '
                
                for x in range(0, 512, 20):
                    y = 256 + amplitude * math.sin(frequency * x * math.pi / 180)
                    path_data += f'L {x},{y} '
                
                path_data += 'L 512,256 L 512,512 L 0,512 Z'
                
                ET.SubElement(svg, 'path', {
                    'd': path_data,
                    'fill': colors[i+1],
                    'opacity': str(random.uniform(0.6, 0.9)),
                    'transform': f'rotate({random.randint(0, 360)} 256 256)'
                })
                
        elif shape_type == 'curves':
            # Create curved designs
            for i in range(3):
                radius = random.randint(100, 200)
                stroke_width = random.randint(20, 60)
                
                ET.SubElement(svg, 'circle', {
                    'cx': '256',
                    'cy': '256',
                    'r': str(radius),
                    'fill': 'none',
                    'stroke': colors[i % len(colors)],
                    'stroke-width': str(stroke_width),
                    'opacity': str(random.uniform(0.6, 0.9))
                })

    def _generate_tech_avatar(self, svg):
        """Generate a technology-themed avatar"""
        # Use tech color palette
        bg_color = random.choice(['#0A1929', '#1A202C', '#172A45', '#1E293B'])
        accent_color = random.choice(['#38BDF8', '#4F46E5', '#14B8A6', '#8B5CF6'])
        
        # Background
        ET.SubElement(svg, 'rect', {
            'width': '512',
            'height': '512',
            'fill': bg_color
        })
        
        # Choose a tech pattern
        pattern_type = random.choice(['circuit', 'binary', 'nodes'])
        
        if pattern_type == 'circuit':
            # Create circuit-like pattern
            g = ET.SubElement(svg, 'g', {'fill': 'none', 'stroke': accent_color, 'stroke-width': '3'})
            
            # Create a grid of circuit lines
            for _ in range(15):
                x1 = random.randint(50, 462)
                y1 = random.randint(50, 462)
                
                # Decide direction
                if random.random() > 0.5:
                    # Horizontal then vertical
                    x2 = random.randint(50, 462)
                    ET.SubElement(g, 'line', {
                        'x1': str(x1),
                        'y1': str(y1),
                        'x2': str(x2),
                        'y2': str(y1)
                    })
                    
                    y2 = random.randint(50, 462)
                    ET.SubElement(g, 'line', {
                        'x1': str(x2),
                        'y1': str(y1),
                        'x2': str(x2),
                        'y2': str(y2)
                    })
                else:
                    # Vertical then horizontal
                    y2 = random.randint(50, 462)
                    ET.SubElement(g, 'line', {
                        'x1': str(x1),
                        'y1': str(y1),
                        'x2': str(x1),
                        'y2': str(y2)
                    })
                    
                    x2 = random.randint(50, 462)
                    ET.SubElement(g, 'line', {
                        'x1': str(x1),
                        'y1': str(y2),
                        'x2': str(x2),
                        'y2': str(y2)
                    })
                
                # Add connection circles
                ET.SubElement(svg, 'circle', {
                    'cx': str(x1),
                    'cy': str(y1),
                    'r': '5',
                    'fill': accent_color
                })
                
                ET.SubElement(svg, 'circle', {
                    'cx': str(x2),
                    'cy': str(y2),
                    'r': '5',
                    'fill': accent_color
                })
                
        elif pattern_type == 'binary':
            # Create binary pattern
            g = ET.SubElement(svg, 'g', {'fill': accent_color, 'font-family': 'monospace', 'font-size': '16'})
            
            for _ in range(200):
                x = random.randint(20, 492)
                y = random.randint(20, 492)
                digit = random.choice(['0', '1'])
                opacity = random.uniform(0.3, 1.0)
                
                ET.SubElement(g, 'text', {
                    'x': str(x),
                    'y': str(y),
                    'opacity': str(opacity)
                }).text = digit
                
        elif pattern_type == 'nodes':
            # Create a network of nodes
            g = ET.SubElement(svg, 'g', {'fill': 'none', 'stroke': accent_color, 'stroke-width': '2'})
            
            # Create nodes
            nodes = []
            for _ in range(random.randint(6, 12)):
                x = random.randint(80, 432)
                y = random.randint(80, 432)
                nodes.append((x, y))
                
                ET.SubElement(svg, 'circle', {
                    'cx': str(x),
                    'cy': str(y),
                    'r': '8',
                    'fill': accent_color
                })
            
            # Connect nodes
            for i in range(len(nodes)):
                # Connect to 2-3 other nodes
                connections = random.randint(1, 3)
                connected = set()
                
                for _ in range(connections):
                    # Choose a random node to connect to
                    target = random.randint(0, len(nodes) - 1)
                    
                    # Avoid self-connections and duplicates
                    if target != i and target not in connected:
                        connected.add(target)
                        
                        ET.SubElement(g, 'line', {
                            'x1': str(nodes[i][0]),
                            'y1': str(nodes[i][1]),
                            'x2': str(nodes[target][0]),
                            'y2': str(nodes[target][1]),
                            'opacity': '0.6'
                        })

    def _generate_cybersecurity_avatar(self, svg):
        """Generate a cybersecurity-themed avatar"""
        # Use security color palette
        bg_color = random.choice(['#121212', '#1A1A1A', '#0C0C0C', '#232323'])
        accent_color = random.choice(['#00FF41', '#4CAF50', '#FF5252', '#2196F3'])
        
        # Background
        ET.SubElement(svg, 'rect', {
            'width': '512',
            'height': '512',
            'fill': bg_color
        })
        
        # Choose a security pattern
        pattern_type = random.choice(['lock', 'shield', 'matrix', 'fingerprint'])
        
        if pattern_type == 'lock':
            # Create a lock symbol
            # Lock body
            ET.SubElement(svg, 'rect', {
                'x': '156',
                'y': '226',
                'width': '200',
                'height': '160',
                'rx': '20',
                'fill': accent_color,
                'opacity': '0.8'
            })
            
            # Lock shackle
            ET.SubElement(svg, 'path', {
                'd': 'M 196 226 L 196 176 C 196 126, 316 126, 316 176 L 316 226',
                'fill': 'none',
                'stroke': accent_color,
                'stroke-width': '40',
                'opacity': '0.9'
            })
            
        elif pattern_type == 'shield':
            # Create a shield symbol
            ET.SubElement(svg, 'path', {
                'd': 'M 256 96 L 386 156 C 386 326, 336 386, 256 416 C 176 386, 126 326, 126 156 L 256 96',
                'fill': accent_color,
                'opacity': '0.8'
            })
            
            # Add design elements
            if random.random() > 0.5:
                # Checkmark
                ET.SubElement(svg, 'path', {
                    'd': 'M 206 256 L 236 286 L 306 216',
                    'fill': 'none',
                    'stroke': bg_color,
                    'stroke-width': '20',
                    'stroke-linecap': 'round',
                    'stroke-linejoin': 'round'
                })
            else:
                # Keyhole
                ET.SubElement(svg, 'circle', {
                    'cx': '256',
                    'cy': '246',
                    'r': '30',
                    'fill': bg_color
                })
                ET.SubElement(svg, 'rect', {
                    'x': '241',
                    'y': '246',
                    'width': '30',
                    'height': '40',
                    'fill': bg_color
                })
                
        elif pattern_type == 'matrix':
            # Create matrix/code rain effect
            g = ET.SubElement(svg, 'g', {'fill': accent_color, 'font-family': 'monospace', 'font-size': '14'})
            
            # Characters to use in the matrix
            chars = 'ABCDEF0123456789@#$%^&*()'
            
            # Create columns of falling characters
            columns = random.randint(10, 20)
            column_width = 512 / columns
            
            for col in range(columns):
                x = col * column_width + column_width / 2
                
                # Each column has a random number of characters
                char_count = random.randint(10, 30)
                
                for i in range(char_count):
                    y = (i * 20) % 512
                    opacity = 1.0 - (i / char_count)
                    char = random.choice(chars)
                    
                    ET.SubElement(g, 'text', {
                        'x': str(x),
                        'y': str(y),
                        'opacity': str(opacity)
                    }).text = char
        
        elif pattern_type == 'fingerprint':
            # Create a fingerprint-like pattern
            center_x, center_y = 256, 256
            
            for i in range(8):
                radius = 40 + i * 20
                
                # Calculate path for a nearly complete circle with a random gap
                gap_angle = random.uniform(0, math.pi/4)
                gap_position = random.uniform(0, 2 * math.pi)
                
                start_angle = gap_position + gap_angle
                end_angle = gap_position + 2 * math.pi - gap_angle
                
                # Create the path data
                path_data = f"M {center_x + radius * math.cos(start_angle)},{center_y + radius * math.sin(start_angle)}"
                
                # Add arc
                large_arc = 1  # always use large arc (> 180 degrees)
                sweep = 1      # clockwise
                
                end_x = center_x + radius * math.cos(end_angle)
                end_y = center_y + radius * math.sin(end_angle)
                
                path_data += f" A {radius},{radius} 0 {large_arc} {sweep} {end_x},{end_y}"
                
                # Add some random "breaks" in the fingerprint lines
                for _ in range(random.randint(0, 3)):
                    break_angle = random.uniform(start_angle, end_angle)
                    break_length = random.uniform(0.1, 0.3)
                    
                    break_start = break_angle
                    break_end = break_angle + break_length
                    
                    if break_end <= end_angle:
                        # Need to split the arc into two parts
                        break_start_x = center_x + radius * math.cos(break_start)
                        break_start_y = center_y + radius * math.sin(break_start)
                        break_end_x = center_x + radius * math.cos(break_end)
                        break_end_y = center_y + radius * math.sin(break_end)
                        
                        # Replace original arc with two arcs with a gap
                        path_data = path_data.replace(
                            f" A {radius},{radius} 0 {large_arc} {sweep} {end_x},{end_y}",
                            f" A {radius},{radius} 0 0 {sweep} {break_start_x},{break_start_y} M {break_end_x},{break_end_y} A {radius},{radius} 0 {large_arc} {sweep} {end_x},{end_y}"
                        )
                
                ET.SubElement(svg, 'path', {
                    'd': path_data,
                    'fill': 'none',
                    'stroke': accent_color,
                    'stroke-width': '3',
                    'opacity': str(0.5 + i * 0.05)
                })

    def _generate_minimal_avatar(self, svg):
        """Generate a minimal, clean avatar design"""
        # Choose a clean color palette
        bg_color = random.choice(['#FFFFFF', '#F5F5F5', '#FAFAFA', '#F0F0F0'])
        accent_color = random.choice(['#333333', '#555555', '#3498DB', '#2ECC71', '#E74C3C'])
        
        # Background
        ET.SubElement(svg, 'rect', {
            'width': '512',
            'height': '512',
            'fill': bg_color
        })
        
        # Choose a minimal pattern
        pattern_type = random.choice(['lines', 'single-shape', 'corner'])
        
        if pattern_type == 'lines':
            # Create simple line pattern
            g = ET.SubElement(svg, 'g', {'stroke': accent_color, 'stroke-width': str(random.randint(2, 8))})
            
            line_count = random.randint(3, 8)
            for i in range(line_count):
                # Horizontal or vertical lines
                if random.random() > 0.5:
                    # Horizontal
                    y = 50 + i * (412 / line_count)
                    ET.SubElement(g, 'line', {
                        'x1': '50',
                        'y1': str(y),
                        'x2': '462',
                        'y2': str(y)
                    })
                else:
                    # Vertical
                    x = 50 + i * (412 / line_count)
                    ET.SubElement(g, 'line', {
                        'x1': str(x),
                        'y1': '50',
                        'x2': str(x),
                        'y2': '462'
                    })
                    
        elif pattern_type == 'single-shape':
            # Just a simple centered shape
            shape_type = random.choice(['circle', 'square', 'triangle'])
            
            if shape_type == 'circle':
                ET.SubElement(svg, 'circle', {
                    'cx': '256',
                    'cy': '256',
                    'r': str(random.randint(100, 180)),
                    'fill': accent_color
                })
                
            elif shape_type == 'square':
                size = random.randint(180, 320)
                ET.SubElement(svg, 'rect', {
                    'x': str(256 - size/2),
                    'y': str(256 - size/2),
                    'width': str(size),
                    'height': str(size),
                    'fill': accent_color
                })
                
            elif shape_type == 'triangle':
                size = random.randint(200, 350)
                height = size * 0.866  # sqrt(3)/2
                
                points = f"{256},{256-height/2} {256-size/2},{256+height/2} {256+size/2},{256+height/2}"
                
                ET.SubElement(svg, 'polygon', {
                    'points': points,
                    'fill': accent_color
                })
                
        elif pattern_type == 'corner':
            # Design with a single corner element
            corner = random.choice(['top-left', 'top-right', 'bottom-left', 'bottom-right'])
            
            if corner == 'top-left':
                ET.SubElement(svg, 'rect', {
                    'x': '0',
                    'y': '0',
                    'width': '256',
                    'height': '256',
                    'fill': accent_color
                })
            elif corner == 'top-right':
                ET.SubElement(svg, 'rect', {
                    'x': '256',
                    'y': '0',
                    'width': '256',
                    'height': '256',
                    'fill': accent_color
                })
            elif corner == 'bottom-left':
                ET.SubElement(svg, 'rect', {
                    'x': '0',
                    'y': '256',
                    'width': '256',
                    'height': '256',
                    'fill': accent_color
                })
            elif corner == 'bottom-right':
                ET.SubElement(svg, 'rect', {
                    'x': '256',
                    'y': '256',
                    'width': '256',
                    'height': '256',
                    'fill': accent_color
                })

    def _generate_gradient_avatar(self, svg):
        """Generate an avatar with smooth gradients"""
        # Define the gradient
        gradient_type = random.choice(['linear', 'radial'])
        
        # Choose attractive color combinations
        color_pairs = [
            ('#FF416C', '#FF4B2B'),  # Red-Orange
            ('#4776E6', '#8E54E9'),  # Blue-Purple
            ('#00B09B', '#96C93D'),  # Green-Lime
            ('#FDC830', '#F37335'),  # Yellow-Orange
            ('#5433FF', '#20BDFF'),  # Purple-Blue
            ('#2193b0', '#6dd5ed'),  # Blue-Cyan
            ('#834d9b', '#d04ed6'),  # Purple-Pink
            ('#4568DC', '#B06AB3'),  # Blue-Purple
            ('#009FFF', '#ec2F4B'),  # Blue-Red
            ('#654ea3', '#eaafc8'),  # Purple-Pink
        ]
        
        color1, color2 = random.choice(color_pairs)
        
        if gradient_type == 'linear':
            # Linear gradient
            # Define the gradient
            defs = ET.SubElement(svg, 'defs')
            
            # Choose gradient direction
            angle = random.randint(0, 360)
            x1 = str(50 + 50 * math.cos(math.radians(angle)))
            y1 = str(50 + 50 * math.sin(math.radians(angle)))
            x2 = str(50 + 50 * math.cos(math.radians(angle + 180)))
            y2 = str(50 + 50 * math.sin(math.radians(angle + 180)))
            
            linear_gradient = ET.SubElement(defs, 'linearGradient', {
                'id': 'gradient',
                'x1': x1 + '%',
                'y1': y1 + '%',
                'x2': x2 + '%',
                'y2': y2 + '%'
            })
            
            ET.SubElement(linear_gradient, 'stop', {
                'offset': '0%',
                'stop-color': color1
            })
            
            ET.SubElement(linear_gradient, 'stop', {
                'offset': '100%',
                'stop-color': color2
            })
            
            # Apply gradient to background
            ET.SubElement(svg, 'rect', {
                'width': '512',
                'height': '512',
                'fill': 'url(#gradient)'
            })
            
            # Add some subtle overlays
            if random.random() > 0.5:
                num_shapes = random.randint(3, 6)
                for _ in range(num_shapes):
                    opacity = random.uniform(0.05, 0.2)
                    size = random.randint(100, 300)
                    cx = random.randint(0, 512)
                    cy = random.randint(0, 512)
                    
                    ET.SubElement(svg, 'circle', {
                        'cx': str(cx),
                        'cy': str(cy),
                        'r': str(size),
                        'fill': 'white',
                        'opacity': str(opacity)
                    })
            
        elif gradient_type == 'radial':
            # Radial gradient
            defs = ET.SubElement(svg, 'defs')
            
            # Random positioning of gradient center
            cx = random.randint(30, 70)
            cy = random.randint(30, 70)
            
            radial_gradient = ET.SubElement(defs, 'radialGradient', {
                'id': 'gradient',
                'cx': str(cx) + '%',
                'cy': str(cy) + '%',
                'r': '70%',
                'fx': str(cx) + '%',
                'fy': str(cy) + '%'
            })
            
            ET.SubElement(radial_gradient, 'stop', {
                'offset': '0%',
                'stop-color': color1
            })
            
            ET.SubElement(radial_gradient, 'stop', {
                'offset': '100%',
                'stop-color': color2
            })
            
            # Apply gradient to background
            ET.SubElement(svg, 'rect', {
                'width': '512',
                'height': '512',
                'fill': 'url(#gradient)'
            })
            
            # Add some rings
            if random.random() > 0.5:
                center_x, center_y = 256, 256
                for i in range(random.randint(2, 4)):
                    radius = 100 + i * 60
                    ET.SubElement(svg, 'circle', {
                        'cx': str(center_x),
                        'cy': str(center_y),
                        'r': str(radius),
                        'fill': 'none',
                        'stroke': 'white',
                        'stroke-width': '2',
                        'opacity': '0.2'
                    })

    def _hsl_to_hex(self, h, s, l):
        """Convert HSL color values to HEX"""
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return '#{:02x}{:02x}{:02x}'.format(
            int(r * 255), 
            int(g * 255), 
            int(b * 255)
        )

    def _get_random_color(self, opacity=1.0):
        """Generate a random color with given opacity"""
        h = random.random()
        s = random.uniform(0.5, 0.9)
        l = random.uniform(0.4, 0.8)
        
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        
        return f'rgba({int(r*255)}, {int(g*255)}, {int(b*255)}, {opacity})'
        
    def _generate_pixel_avatar(self, svg):
        """Generate a retro pixel art style avatar"""
        # Pixel art settings
        grid_size = random.choice([8, 10, 12, 16])  # Number of pixels per side
        pixel_size = 512 / grid_size
        
        # Choose a color palette
        palette_types = ['gameboy', 'synthwave', 'retro-console', 'monochrome']
        palette_type = random.choice(palette_types)
        
        if palette_type == 'gameboy':
            # GameBoy inspired colors
            colors = [
                '#0f380f',  # Dark green
                '#306230',  # Medium green
                '#8bac0f',  # Light green
                '#9bbc0f',  # Lightest green/yellow
            ]
            bg_color = colors[0]
        elif palette_type == 'synthwave':
            # Synthwave inspired colors
            colors = [
                '#2b213a',  # Dark purple
                '#e83b3b',  # Red
                '#23b2be',  # Cyan
                '#f6d6bd',  # Light peach
                '#c72e8e',  # Pink
            ]
            bg_color = colors[0]
        elif palette_type == 'retro-console':
            # NES/SNES inspired
            colors = [
                '#211640',  # Dark blue
                '#c0c0c0',  # Silver
                '#ff004d',  # Red
                '#29adff',  # Blue
                '#00e756',  # Green
                '#ffccaa',  # Skin tone
            ]
            bg_color = colors[0]
        else:  # monochrome
            # Black and white with grays
            base_hue = random.random()
            colors = [
                self._hsl_to_hex(base_hue, 0.8, 0.1),  # Dark
                self._hsl_to_hex(base_hue, 0.6, 0.3),  # Medium dark
                self._hsl_to_hex(base_hue, 0.4, 0.5),  # Medium
                self._hsl_to_hex(base_hue, 0.2, 0.7),  # Light
                self._hsl_to_hex(base_hue, 0.1, 0.9),  # Very light
            ]
            bg_color = colors[0]
            
        # Background
        ET.SubElement(svg, 'rect', {
            'width': '512',
            'height': '512',
            'fill': bg_color
        })
        
        # Choose what to draw
        pixel_pattern = random.choice(['character', 'icon', 'abstract'])
        
        if pixel_pattern == 'character':
            # Create a pixel character face
            # This is a simplified character face with eyes, etc.
            
            # Face/head base (central area)
            face_color = random.choice(colors[1:])
            
            for y in range(grid_size // 3, grid_size - grid_size // 3):
                for x in range(grid_size // 3, grid_size - grid_size // 3):
                    # Skip some pixels for details
                    if random.random() < 0.1:
                        continue
                        
                    ET.SubElement(svg, 'rect', {
                        'x': str(x * pixel_size),
                        'y': str(y * pixel_size),
                        'width': str(pixel_size),
                        'height': str(pixel_size),
                        'fill': face_color
                    })
            
            # Eyes (two pixels)
            eye_color = random.choice([c for c in colors if c != face_color])
            eye_distance = grid_size // 4
            
            # Left eye
            ET.SubElement(svg, 'rect', {
                'x': str((grid_size // 2 - eye_distance) * pixel_size),
                'y': str((grid_size // 2 - 1) * pixel_size),
                'width': str(pixel_size),
                'height': str(pixel_size),
                'fill': eye_color
            })
            
            # Right eye
            ET.SubElement(svg, 'rect', {
                'x': str((grid_size // 2 + eye_distance - 1) * pixel_size),
                'y': str((grid_size // 2 - 1) * pixel_size),
                'width': str(pixel_size),
                'height': str(pixel_size),
                'fill': eye_color
            })
            
            # Mouth (2-3 pixels in a row)
            mouth_width = random.randint(2, 3)
            mouth_y = grid_size // 2 + 1
            mouth_start_x = grid_size // 2 - mouth_width // 2
            
            for i in range(mouth_width):
                ET.SubElement(svg, 'rect', {
                    'x': str((mouth_start_x + i) * pixel_size),
                    'y': str(mouth_y * pixel_size),
                    'width': str(pixel_size),
                    'height': str(pixel_size),
                    'fill': eye_color
                })
                
        elif pixel_pattern == 'icon':
            # Create a pixel icon/logo
            main_color = random.choice(colors[1:])
            
            icon_type = random.choice(['star', 'heart', 'simple-face', 'key', 'sword'])
            
            if icon_type == 'star':
                # Simple 5-point star shape approximation
                center_x = grid_size // 2
                center_y = grid_size // 2
                
                # Star pattern in a 5x5 grid centered at (center_x, center_y)
                star_pattern = [
                    (0, 2), (1, 1), (1, 3), (2, 0), 
                    (2, 4), (3, 1), (3, 3), (4, 2),
                    (2, 1), (2, 2), (2, 3)
                ]
                
                for dx, dy in star_pattern:
                    ET.SubElement(svg, 'rect', {
                        'x': str((center_x - 2 + dx) * pixel_size),
                        'y': str((center_y - 2 + dy) * pixel_size),
                        'width': str(pixel_size),
                        'height': str(pixel_size),
                        'fill': main_color
                    })
            
            elif icon_type == 'heart':
                # Simple heart shape approximation
                center_x = grid_size // 2
                center_y = grid_size // 2
                
                # Heart pattern in a 5x5 grid centered at (center_x, center_y)
                heart_pattern = [
                    (1, 1), (1, 2), (3, 1), (3, 2),
                    (0, 2), (4, 2),
                    (1, 3), (2, 3), (3, 3),
                    (2, 4)
                ]
                
                for dx, dy in heart_pattern:
                    ET.SubElement(svg, 'rect', {
                        'x': str((center_x - 2 + dx) * pixel_size),
                        'y': str((center_y - 2 + dy) * pixel_size),
                        'width': str(pixel_size),
                        'height': str(pixel_size),
                        'fill': main_color
                    })
            
            elif icon_type == 'simple-face':
                # Simple smiley face
                center_x = grid_size // 2
                center_y = grid_size // 2
                radius = grid_size // 3
                
                # Draw a circle of pixels
                for y in range(grid_size):
                    for x in range(grid_size):
                        dx = x - center_x
                        dy = y - center_y
                        distance = (dx*dx + dy*dy) ** 0.5
                        
                        if radius - 1 <= distance <= radius:
                            ET.SubElement(svg, 'rect', {
                                'x': str(x * pixel_size),
                                'y': str(y * pixel_size),
                                'width': str(pixel_size),
                                'height': str(pixel_size),
                                'fill': main_color
                            })
                
                # Eyes
                eye_color = random.choice([c for c in colors if c != main_color])
                
                # Left eye
                ET.SubElement(svg, 'rect', {
                    'x': str((center_x - radius//2) * pixel_size),
                    'y': str((center_y - radius//2) * pixel_size),
                    'width': str(pixel_size),
                    'height': str(pixel_size),
                    'fill': eye_color
                })
                
                # Right eye
                ET.SubElement(svg, 'rect', {
                    'x': str((center_x + radius//2) * pixel_size),
                    'y': str((center_y - radius//2) * pixel_size),
                    'width': str(pixel_size),
                    'height': str(pixel_size),
                    'fill': eye_color
                })
                
                # Smile
                for i in range(3):
                    ET.SubElement(svg, 'rect', {
                        'x': str((center_x - 1 + i) * pixel_size),
                        'y': str((center_y + radius//2) * pixel_size),
                        'width': str(pixel_size),
                        'height': str(pixel_size),
                        'fill': eye_color
                    })
                    
            elif icon_type == 'key':
                # Simple key icon
                center_x = grid_size // 2
                center_y = grid_size // 2
                
                # Key head (circle)
                key_pattern = []
                
                # Circle for key head
                radius = grid_size // 5
                for y in range(grid_size):
                    for x in range(grid_size):
                        dx = x - (center_x - radius)
                        dy = y - center_y
                        distance = (dx*dx + dy*dy) ** 0.5
                        
                        if distance <= radius:
                            key_pattern.append((x, y))
                
                # Key stem
                for i in range(radius * 2 + 2):
                    key_pattern.append((center_x + i, center_y))
                
                # Key teeth
                key_pattern.append((center_x + radius + 1, center_y - 1))
                key_pattern.append((center_x + radius + 2, center_y - 1))
                
                # Draw the key
                for x, y in key_pattern:
                    if 0 <= x < grid_size and 0 <= y < grid_size:
                        ET.SubElement(svg, 'rect', {
                            'x': str(x * pixel_size),
                            'y': str(y * pixel_size),
                            'width': str(pixel_size),
                            'height': str(pixel_size),
                            'fill': main_color
                        })
            
            elif icon_type == 'sword':
                # Simple sword icon
                center_x = grid_size // 2
                center_y = grid_size // 2
                
                # Blade
                for i in range(grid_size // 2 - 1):
                    ET.SubElement(svg, 'rect', {
                        'x': str(center_x * pixel_size),
                        'y': str(i * pixel_size),
                        'width': str(pixel_size),
                        'height': str(pixel_size),
                        'fill': random.choice(colors[1:])
                    })
                
                # Guard
                guard_color = random.choice([c for c in colors if c != colors[0]])
                for i in range(-2, 3):
                    ET.SubElement(svg, 'rect', {
                        'x': str((center_x + i) * pixel_size),
                        'y': str((grid_size // 2 - 1) * pixel_size),
                        'width': str(pixel_size),
                        'height': str(pixel_size),
                        'fill': guard_color
                    })
                
                # Handle
                handle_color = random.choice([c for c in colors if c != colors[0] and c != guard_color])
                for i in range(grid_size // 4):
                    ET.SubElement(svg, 'rect', {
                        'x': str(center_x * pixel_size),
                        'y': str((grid_size // 2 + i) * pixel_size),
                        'width': str(pixel_size),
                        'height': str(pixel_size),
                        'fill': handle_color
                    })
                
                # Pommel
                ET.SubElement(svg, 'rect', {
                    'x': str((center_x - 1) * pixel_size),
                    'y': str((grid_size // 2 + grid_size // 4) * pixel_size),
                    'width': str(pixel_size * 3),
                    'height': str(pixel_size),
                    'fill': guard_color
                })
        
        else:  # abstract
            # Create abstract pixel patterns
            for i in range(random.randint(20, 50)):
                x = random.randint(0, grid_size - 1)
                y = random.randint(0, grid_size - 1)
                color = random.choice(colors[1:])
                
                ET.SubElement(svg, 'rect', {
                    'x': str(x * pixel_size),
                    'y': str(y * pixel_size),
                    'width': str(pixel_size),
                    'height': str(pixel_size),
                    'fill': color
                })
                
                # Sometimes add a small pattern around this pixel
                if random.random() < 0.3:
                    pattern_size = random.randint(2, 3)
                    for dx in range(pattern_size):
                        for dy in range(pattern_size):
                            nx = x + dx
                            ny = y + dy
                            if 0 <= nx < grid_size and 0 <= ny < grid_size and random.random() < 0.7:
                                ET.SubElement(svg, 'rect', {
                                    'x': str(nx * pixel_size),
                                    'y': str(ny * pixel_size),
                                    'width': str(pixel_size),
                                    'height': str(pixel_size),
                                    'fill': color
                                })

    def _generate_neon_avatar(self, svg):
        """Generate a vibrant neon-styled avatar"""
        # Dark background
        bg_color = random.choice(['#121212', '#0D0221', '#171717', '#0D0D0D', '#231651'])
        
        ET.SubElement(svg, 'rect', {
            'width': '512',
            'height': '512',
            'fill': bg_color
        })
        
        # Add filter for glow effect
        defs = ET.SubElement(svg, 'defs')
        
        # Define glow filter
        glow_filter = ET.SubElement(defs, 'filter', {
            'id': 'neon-glow',
            'x': '-50%',
            'y': '-50%',
            'width': '200%',
            'height': '200%'
        })
        
        ET.SubElement(glow_filter, 'feGaussianBlur', {
            'stdDeviation': '10',
            'result': 'blur'
        })
        
        # Neon colors
        neon_colors = [
            '#FF00FF',  # Magenta
            '#00FFFF',  # Cyan
            '#FF3131',  # Neon Red
            '#39FF14',  # Neon Green
            '#FF10F0',  # Pink
            '#FFF01F',  # Yellow
            '#7DF9FF',  # Electric Blue
        ]
        
        # Choose design type
        design_type = random.choice(['shapes', 'outlines', 'text', 'grid'])
        
        if design_type == 'shapes':
            # Neon geometric shapes
            shape_count = random.randint(2, 4)
            
            for i in range(shape_count):
                color = random.choice(neon_colors)
                shape_type = random.choice(['circle', 'rect', 'polygon'])
                
                g = ET.SubElement(svg, 'g', {'filter': 'url(#neon-glow)'})
                
                if shape_type == 'circle':
                    cx = random.randint(128, 384)
                    cy = random.randint(128, 384)
                    r = random.randint(40, 100)
                    
                    ET.SubElement(g, 'circle', {
                        'cx': str(cx),
                        'cy': str(cy),
                        'r': str(r),
                        'fill': 'none',
                        'stroke': color,
                        'stroke-width': '4'
                    })
                    
                elif shape_type == 'rect':
                    x = random.randint(100, 300)
                    y = random.randint(100, 300)
                    width = random.randint(80, 200)
                    height = random.randint(80, 200)
                    
                    ET.SubElement(g, 'rect', {
                        'x': str(x),
                        'y': str(y),
                        'width': str(width),
                        'height': str(height),
                        'fill': 'none',
                        'stroke': color,
                        'stroke-width': '4'
                    })
                    
                elif shape_type == 'polygon':
                    # Create triangle or other polygon
                    points = []
                    sides = random.randint(3, 6)
                    center_x, center_y = 256, 256
                    radius = random.randint(80, 150)
                    
                    for j in range(sides):
                        angle = j * (2 * math.pi / sides)
                        px = center_x + radius * math.cos(angle)
                        py = center_y + radius * math.sin(angle)
                        points.append(f"{px},{py}")
                    
                    ET.SubElement(g, 'polygon', {
                        'points': ' '.join(points),
                        'fill': 'none',
                        'stroke': color,
                        'stroke-width': '4'
                    })
        
        elif design_type == 'outlines':
            # Neon outline design
            color = random.choice(neon_colors)
            
            g = ET.SubElement(svg, 'g', {'filter': 'url(#neon-glow)'})
            
            # Create a random path
            path_data = 'M 256,156'
            
            # Create a series of curves
            points = random.randint(5, 8)
            for i in range(points):
                angle = i * (2 * math.pi / points)
                radius = random.randint(80, 180)
                
                # Control points
                cp1x = 256 + radius * 0.8 * math.cos(angle + 0.2)
                cp1y = 256 + radius * 0.8 * math.sin(angle + 0.2)
                cp2x = 256 + radius * 0.8 * math.cos(angle + 0.4)
                cp2y = 256 + radius * 0.8 * math.sin(angle + 0.4)
                
                # End point
                x = 256 + radius * math.cos(angle + 0.6)
                y = 256 + radius * math.sin(angle + 0.6)
                
                path_data += f' C {cp1x},{cp1y} {cp2x},{cp2y} {x},{y}'
            
            # Close the path
            path_data += ' Z'
            
            ET.SubElement(g, 'path', {
                'd': path_data,
                'fill': 'none',
                'stroke': color,
                'stroke-width': '4'
            })
            
        elif design_type == 'text':
            # Neon text-inspired design (not actual text, just symbols)
            color = random.choice(neon_colors)
            
            g = ET.SubElement(svg, 'g', {'filter': 'url(#neon-glow)'})
            
            symbol_type = random.choice(['arrows', 'equals', 'brackets', 'slashes'])
            
            if symbol_type == 'arrows':
                # Create arrow-like symbols
                for _ in range(random.randint(2, 4)):
                    x = random.randint(128, 384)
                    y = random.randint(128, 384)
                    size = random.randint(60, 120)
                    rotation = random.randint(0, 360)
                    
                    # Arrow path
                    path_data = f'M {x},{y} l {size},0 l -{size/4},-{size/4} m 0,{size/2} l {size/4},-{size/4}'
                    
                    ET.SubElement(g, 'path', {
                        'd': path_data,
                        'fill': 'none',
                        'stroke': color,
                        'stroke-width': '4',
                        'transform': f'rotate({rotation} {x} {y})'
                    })
                    
            elif symbol_type == 'equals':
                # Create equal-like symbols
                for _ in range(random.randint(3, 6)):
                    x = random.randint(128, 384)
                    y = random.randint(128, 384)
                    width = random.randint(60, 150)
                    gap = random.randint(20, 40)
                    rotation = random.randint(0, 360)
                    
                    g2 = ET.SubElement(g, 'g', {'transform': f'rotate({rotation} {x} {y})'})
                    
                    # Top line
                    ET.SubElement(g2, 'line', {
                        'x1': str(x - width/2),
                        'y1': str(y - gap/2),
                        'x2': str(x + width/2),
                        'y2': str(y - gap/2),
                        'stroke': color,
                        'stroke-width': '4'
                    })
                    
                    # Bottom line
                    ET.SubElement(g2, 'line', {
                        'x1': str(x - width/2),
                        'y1': str(y + gap/2),
                        'x2': str(x + width/2),
                        'y2': str(y + gap/2),
                        'stroke': color,
                        'stroke-width': '4'
                    })
                    
            elif symbol_type == 'brackets':
                # Create bracket-like symbols
                for _ in range(random.randint(2, 4)):
                    x = random.randint(128, 384)
                    y = random.randint(128, 384)
                    width = random.randint(40, 80)
                    height = random.randint(80, 150)
                    rotation = random.randint(0, 360)
                    
                    g2 = ET.SubElement(g, 'g', {'transform': f'rotate({rotation} {x} {y})'})
                    
                    # Left bracket
                    path_data = f'M {x-width/2},{y-height/2} h {width/3} m 0,{height} h -{width/3}'
                    ET.SubElement(g2, 'path', {
                        'd': path_data,
                        'fill': 'none',
                        'stroke': color,
                        'stroke-width': '4'
                    })
                    
                    # Right bracket
                    path_data = f'M {x+width/2},{y-height/2} h -{width/3} m 0,{height} h {width/3}'
                    ET.SubElement(g2, 'path', {
                        'd': path_data,
                        'fill': 'none',
                        'stroke': color,
                        'stroke-width': '4'
                    })
                    
                    # Vertical lines
                    ET.SubElement(g2, 'line', {
                        'x1': str(x - width/2),
                        'y1': str(y - height/2),
                        'x2': str(x - width/2),
                        'y2': str(y + height/2),
                        'stroke': color,
                        'stroke-width': '4'
                    })
                    
                    ET.SubElement(g2, 'line', {
                        'x1': str(x + width/2),
                        'y1': str(y - height/2),
                        'x2': str(x + width/2),
                        'y2': str(y + height/2),
                        'stroke': color,
                        'stroke-width': '4'
                    })
            
            elif symbol_type == 'slashes':
                # Create slash-like symbols
                for _ in range(random.randint(4, 8)):
                    x = random.randint(128, 384)
                    y = random.randint(128, 384)
                    length = random.randint(80, 150)
                    rotation = random.randint(0, 360)
                    
                    g2 = ET.SubElement(g, 'g', {'transform': f'rotate({rotation} {x} {y})'})
                    
                    # Slash line
                    ET.SubElement(g2, 'line', {
                        'x1': str(x - length/2),
                        'y1': str(y),
                        'x2': str(x + length/2),
                        'y2': str(y),
                        'stroke': color,
                        'stroke-width': '4'
                    })
        
        elif design_type == 'grid':
            # Neon grid design
            color1 = random.choice(neon_colors)
            color2 = random.choice([c for c in neon_colors if c != color1])
            
            g = ET.SubElement(svg, 'g', {'filter': 'url(#neon-glow)'})
            
            # Number of grid lines
            grid_spacing = random.randint(60, 100)
            
            # Horizontal lines
            for i in range(0, 512, grid_spacing):
                ET.SubElement(g, 'line', {
                    'x1': '0',
                    'y1': str(i),
                    'x2': '512',
                    'y2': str(i),
                    'stroke': color1,
                    'stroke-width': '2'
                })
            
            # Vertical lines
            for i in range(0, 512, grid_spacing):
                ET.SubElement(g, 'line', {
                    'x1': str(i),
                    'y1': '0',
                    'x2': str(i),
                    'y2': '512',
                    'stroke': color2,
                    'stroke-width': '2'
                })
            
            # Add a central element
            central_element = random.choice(['circle', 'sun', 'triangle'])
            
            if central_element == 'circle':
                ET.SubElement(g, 'circle', {
                    'cx': '256',
                    'cy': '256',
                    'r': '80',
                    'fill': 'none',
                    'stroke': random.choice([color1, color2]),
                    'stroke-width': '6'
                })
            
            elif central_element == 'sun':
                # Circle with rays
                ET.SubElement(g, 'circle', {
                    'cx': '256',
                    'cy': '256',
                    'r': '60',
                    'fill': 'none',
                    'stroke': random.choice([color1, color2]),
                    'stroke-width': '6'
                })
                
                # Rays
                ray_color = random.choice([color1, color2])
                for i in range(8):
                    angle = i * (2 * math.pi / 8)
                    inner_x = 256 + 60 * math.cos(angle)
                    inner_y = 256 + 60 * math.sin(angle)
                    outer_x = 256 + 100 * math.cos(angle)
                    outer_y = 256 + 100 * math.sin(angle)
                    
                    ET.SubElement(g, 'line', {
                        'x1': str(inner_x),
                        'y1': str(inner_y),
                        'x2': str(outer_x),
                        'y2': str(outer_y),
                        'stroke': ray_color,
                        'stroke-width': '6'
                    })
            
            elif central_element == 'triangle':
                # Equilateral triangle
                side = 160
                height = side * 0.866  # sqrt(3)/2
                
                points = f"{256},{256-height/2*0.866} {256-side/2},{256+height/2*0.866} {256+side/2},{256+height/2*0.866}"
                
                ET.SubElement(g, 'polygon', {
                    'points': points,
                    'fill': 'none',
                    'stroke': random.choice([color1, color2]),
                    'stroke-width': '6'
                })
