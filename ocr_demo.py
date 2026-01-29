#!/usr/bin/env python3
"""
Demo script for Family Manager Mobile OCR functionality
Run this to test OCR text parsing without the full mobile app.
"""

def demo_ocr_parsing():
    """Demo the OCR text parsing functionality"""

    # Sample OCR text that might come from a receipt
    sample_texts = [
        "Milk 2L, Bread 1 loaf, Eggs 12 count",
        "Cheese 500g, Apples 6 each, Yogurt 4 pack",
        "Chicken breast 1.5kg, Rice 2kg, Pasta 500g"
    ]

    print("Family Manager Mobile - OCR Demo")
    print("=" * 40)

    for i, text in enumerate(sample_texts, 1):
        print(f"\nDemo {i}: Parsing OCR text")
        print(f"Input: {text}")

        # Parse the text (similar to mobile app logic)
        items = []
        lines = [line.strip() for line in text.split(',') if line.strip()]

        for line in lines:
            if not line:
                continue

            # Each line is already an item (comma-separated at higher level)
            # Parse this single item
            item = {
                'name': line.strip(),
                'category': 'OCR Import',
                'qty': 1.0,
                'unit': 'each',
                'exp_date': None,
                'location': None
            }

            # Try to extract quantity and unit from the name
            name_parts = item['name'].split()
            if len(name_parts) > 1:
                # Look for quantity patterns in the text
                for i, part in enumerate(name_parts):
                    part_lower = part.lower()

                    # Check for quantity + unit patterns
                    if i < len(name_parts) - 1:
                        next_part = name_parts[i + 1].lower()

                        # Handle patterns like "2L", "500g", "1.5kg"
                        if part.isdigit() or ('.' in part and part.replace('.', '').isdigit()):
                            qty = float(part)
                            item['name'] = ' '.join(name_parts[:i] + name_parts[i+2:]) if i+2 < len(name_parts) else ' '.join(name_parts[:i])
                            item['qty'] = qty

                            # Determine unit from next part
                            if 'kg' in next_part:
                                item['unit'] = 'kg'
                            elif 'g' in next_part and 'kg' not in next_part:
                                item['unit'] = 'g'
                            elif 'l' in next_part:
                                item['unit'] = 'liter'
                            elif 'ml' in next_part:
                                item['unit'] = 'ml'
                            elif next_part in ['loaf', 'pack', 'bottle', 'can', 'box', 'each', 'count']:
                                item['unit'] = next_part
                            else:
                                item['unit'] = 'each'
                            break

                    # Handle patterns where quantity/unit is at the end
                    elif i == len(name_parts) - 1:
                        # Check for embedded units like "2L", "500g"
                        if any(unit in part_lower for unit in ['kg', 'g', 'l', 'ml']):
                            # Extract number and unit
                            num_part = ''.join([c for c in part if c.isdigit() or c == '.'])
                            if num_part:
                                qty = float(num_part)
                                item['name'] = ' '.join(name_parts[:-1])
                                item['qty'] = qty

                                if 'kg' in part_lower:
                                    item['unit'] = 'kg'
                                elif 'g' in part_lower and 'kg' not in part_lower:
                                    item['unit'] = 'g'
                                elif 'l' in part_lower:
                                    item['unit'] = 'liter'
                                elif 'ml' in part_lower:
                                    item['unit'] = 'ml'
                                break

                        # Check for plain numbers or unit words
                        elif part.isdigit():
                            item['qty'] = float(part)
                            item['unit'] = 'count'
                            item['name'] = ' '.join(name_parts[:-1])
                            break
                        elif part_lower in ['loaf', 'pack', 'bottle', 'can', 'box', 'each', 'count']:
                            item['unit'] = part_lower
                            item['qty'] = 1.0
                            item['name'] = ' '.join(name_parts[:-1])
                            break

            items.append(item)

        print("Parsed items:")
        for item in items:
            print(f"  - {item['name']}: {item['qty']} {item['unit']}")

if __name__ == '__main__':
    demo_ocr_parsing()