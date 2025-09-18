from django import template
import hashlib

register = template.Library()

@register.filter
def hash_to_color(value):
    """Convert a string to a consistent hex color."""
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEEAD',
             '#D4A5A5', '#9B59B6', '#3498DB', '#1ABC9C', '#F1C40F']
    hash_object = hashlib.md5(value.encode())
    index = int(hash_object.hexdigest(), 16) % len(colors)
    return colors[index]
    return hash_object.hexdigest()[:6]


from django import template

register = template.Library()

@register.filter
def split(value, delimiter):
    """Split a string by delimiter"""
    if value:
        return value.split(delimiter)
    return []

@register.filter
def trim(value):
    """Remove whitespace from string"""
    if value:
        return value.strip()
    return value

@register.filter
def role_display(value):
    """Map internal role keys to human-friendly display names."""
    mapping = {
        'admin': 'Admin',
        'employee': 'Technician',
        'employee_rd': 'R&D Technician',
        'manager': 'Site Manager',
        'company': 'Technical Manager',
        'team_lead': 'NDT Team Leader',
    }
    return mapping.get(value, value)