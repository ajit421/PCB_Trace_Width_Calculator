def pcb_trace_calculator(
    current, 
    thickness_value, 
    thickness_unit, 
    length_value, 
    length_unit, 
    temp_rise_value, 
    temp_rise_unit
):
    # Convert temperature rise to °C
    if temp_rise_unit == 'F':
        delta_T = temp_rise_value * 5/9
    elif temp_rise_unit == 'C':
        delta_T = temp_rise_value
    
    # Handle zero current case
    if current == 0:
        zero_result = {
            'width': {'mil': 0, 'mm': 0, 'µm': 0},
            'resistance': float('inf'),
            'voltage_drop': 0,
            'power_loss': 0
        }
        return {'internal_layers': zero_result, 'external_layers': zero_result}
    
    # Validate temperature rise when current is present
    if delta_T <= 0:
        raise ValueError("Temperature rise must be positive when current > 0")
    
    # Convert thickness to oz
    if thickness_unit == 'oz':
        t_oz = thickness_value
    elif thickness_unit == 'mil':
        t_oz = thickness_value * (25.4 / 34.79)
    elif thickness_unit == 'mm':
        t_oz = thickness_value * (1000 / 34.79)
    elif thickness_unit == 'µm':
        t_oz = thickness_value / 34.79
    
    # Convert length to meters
    if length_unit == 'm':
        length_m = length_value
    elif length_unit == 'in':
        length_m = length_value * 0.0254
    elif length_unit == 'ft':
        length_m = length_value * 0.3048
    elif length_unit == 'mil':
        length_m = length_value * 2.54e-5
    elif length_unit == 'mm':
        length_m = length_value * 0.001
    elif length_unit == 'µm':
        length_m = length_value * 1e-6
    elif length_unit == 'cm':
        length_m = length_value * 0.01
    
    # Copper resistivity (Ω·m)
    rho = 1.7e-8
    
    # Calculate cross-sectional area (mil²)
    # Internal layers: k=0.024, b=0.44, c=0.725
    A_int = (current / (0.024 * (delta_T ** 0.44))) ** (1/0.725)
    # External layers: k=0.048, b=0.44, c=0.725
    A_ext = (current / (0.048 * (delta_T ** 0.44))) ** (1/0.725)
    
    # Calculate trace width (mil)
    W_int_mil = A_int / (t_oz * 1.378)
    W_ext_mil = A_ext / (t_oz * 1.378)
    
    # Convert width to mm and µm
    W_int_mm = W_int_mil * 0.0254
    W_int_um = W_int_mil * 25.4
    W_ext_mm = W_ext_mil * 0.0254
    W_ext_um = W_ext_mil * 25.4
    
    # Calculate resistance (Ω)
    A_int_m2 = A_int * 6.4516e-10
    A_ext_m2 = A_ext * 6.4516e-10
    
    R_int = (rho * length_m) / A_int_m2
    R_ext = (rho * length_m) / A_ext_m2
    
    # Calculate voltage drop (V)
    V_int = current * R_int
    V_ext = current * R_ext
    
    # Calculate power loss (W)
    P_int = (current ** 2) * R_int
    P_ext = (current ** 2) * R_ext
    
    # Prepare results with full precision
    internal = {
        'width': {
            'mil': W_int_mil,
            'mm': W_int_mm,
            'µm': W_int_um
        },
        'resistance': R_int,
        'voltage_drop': V_int,
        'power_loss': P_int
    }
    
    external = {
        'width': {
            'mil': W_ext_mil,
            'mm': W_ext_mm,
            'µm': W_ext_um
        },
        'resistance': R_ext,
        'voltage_drop': V_ext,
        'power_loss': P_ext
    }
    
    return {
        'internal_layers': internal,
        'external_layers': external
    }

def get_user_input():
    print("=== PCB Trace Width Calculator ===")
    print("Based on IPC-2221 Standards\n")
    
    # Get current input
    current = float(input("Enter Current (A): "))
    
    # Get ambient temperature input
    print("\nAmbient Temperature Units:")
    print("1. °C")
    print("2. °F")
    ambient_unit = input("Choose unit (1-2): ")
    ambient_value = float(input("Enter Ambient Temperature: "))
    ambient_unit = 'C' if ambient_unit == '1' else 'F'
    
    # Get thickness input
    print("\nThickness Units:")
    print("1. oz/ft² (oz)")
    print("2. mil")
    print("3. mm")
    print("4. µm")
    thickness_unit = input("Choose unit (1-4): ")
    thickness_value = float(input("Enter Thickness value: "))
    units_map = {'1': 'oz', '2': 'mil', '3': 'mm', '4': 'µm'}
    thickness_unit = units_map.get(thickness_unit, 'oz')
    
    # Get length input
    print("\nLength Units:")
    print("1. in")
    print("2. ft")
    print("3. mil")
    print("4. mm")
    print("5. µm")
    print("6. cm")
    print("7. m")
    length_unit = input("Choose unit (1-7): ")
    length_value = float(input("Enter Trace Length value: "))
    units_map = {'1': 'in', '2': 'ft', '3': 'mil', '4': 'mm', '5': 'µm', '6': 'cm', '7': 'm'}
    length_unit = units_map.get(length_unit, 'm')
    
    # Get temperature rise input
    print("\nTemperature Rise Units:")
    print("1. °C")
    print("2. °F")
    temp_rise_unit = input("Choose unit (1-2): ")
    temp_rise_value = float(input("Enter Temperature Rise value: "))
    temp_rise_unit = 'C' if temp_rise_unit == '1' else 'F'
    
    return {
        'current': current,
        'ambient_temp': ambient_value,
        'ambient_unit': ambient_unit,
        'thickness_value': thickness_value,
        'thickness_unit': thickness_unit,
        'length_value': length_value,
        'length_unit': length_unit,
        'temp_rise_value': temp_rise_value,
        'temp_rise_unit': temp_rise_unit
    }

def format_high_precision(value):
    """Format a value with 10 decimal places, handling infinity"""
    if value == float('inf'):
        return "Infinity"
    return f"{value:.10f}"

def main():
    while True:
        try:
            # Get user inputs
            inputs = get_user_input()
            
            # Display input summary with high precision
            print("\n=== Input Summary ===")
            print(f"Current: {inputs['current']:.10f} A")
            print(f"Ambient Temperature: {inputs['ambient_temp']:.10f} °{inputs['ambient_unit']}")
            print(f"Copper Thickness: {inputs['thickness_value']:.10f} {inputs['thickness_unit']}")
            print(f"Trace Length: {inputs['length_value']:.10f} {inputs['length_unit']}")
            print(f"Temperature Rise: {inputs['temp_rise_value']:.10f} °{inputs['temp_rise_unit']}")
            
            # Perform calculations
            results = pcb_trace_calculator(
                current=inputs['current'],
                thickness_value=inputs['thickness_value'],
                thickness_unit=inputs['thickness_unit'],
                length_value=inputs['length_value'],
                length_unit=inputs['length_unit'],
                temp_rise_value=inputs['temp_rise_value'],
                temp_rise_unit=inputs['temp_rise_unit']
            )
            
            # Display results with high precision
            print("\n=== Results ===")
            
            # Internal Layers
            print("\nInternal Layers:")
            w = results['internal_layers']['width']
            print(f"Required Trace Width: {format_high_precision(w['mil'])} mil | "
                  f"{format_high_precision(w['mm'])} mm | "
                  f"{format_high_precision(w['µm'])} µm")
            print(f"Resistance: {format_high_precision(results['internal_layers']['resistance'])} Ω")
            print(f"Voltage Drop: {format_high_precision(results['internal_layers']['voltage_drop'])} V")
            print(f"Power Loss: {format_high_precision(results['internal_layers']['power_loss'])} W")
            
            # External Layers
            print("\nExternal Layers in Air:")
            w = results['external_layers']['width']
            print(f"Required Trace Width: {format_high_precision(w['mil'])} mil | "
                  f"{format_high_precision(w['mm'])} mm | "
                  f"{format_high_precision(w['µm'])} µm")
            print(f"Resistance: {format_high_precision(results['external_layers']['resistance'])} Ω")
            print(f"Voltage Drop: {format_high_precision(results['external_layers']['voltage_drop'])} V")
            print(f"Power Loss: {format_high_precision(results['external_layers']['power_loss'])} W")
            
            break
            
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Please try again with valid inputs.\n")
            continue

if __name__ == "__main__":
    main()
    