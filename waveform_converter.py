# waveform_converter.py
import re

def create_value_range(start_val, end_val, steps=4):
    if steps <= 1:
        return (start_val,)
    step_size = (end_val - start_val) / (steps - 1)
    values = tuple(int(round(start_val + i * step_size)) for i in range(steps))
    return values

def parse_waveform_data(data_string, range_steps=4):
    result = {
        "pulse_params": None,
        "rest_time": None,
        "rest_time_seconds": None,
        "frequency_groups": [],
        "intensity_lists": [],
        "loop_counts": [],
        "frequency_sequences": [],
        "combined_sequences": [],
        "final_sequence": []
    }

    pulse_match = re.search(r'\+pulse:(\d+,\d+,\d+)', data_string)
    if pulse_match:
        result["pulse_params"] = pulse_match.group(1)
        rest_time_raw = int(pulse_match.group(1).split(',')[0])
        result["rest_time"] = rest_time_raw
        result["rest_time_seconds"] = round(rest_time_raw / 100.0, 1)

    sections = re.split(r'\+section\+', data_string)
    all_section_sequences = []

    for section in sections:
        freq_match = re.search(r'(\d+,\d+,\d+,\d+,\d+)/', section)
        if not freq_match:
            continue
        freq_params = [int(x) for x in freq_match.group(1).split(',')]
        result["frequency_groups"].append(freq_params)

        intensity_pattern = r'(\d+\.\d+)-'
        intensity_matches = re.findall(intensity_pattern, section)
        intensities = [int(float(x)) for x in intensity_matches]
        result["intensity_lists"].append(intensities)

        expected_seconds = (freq_params[2] + 1) / 10.0
        group_duration = len(intensities) * 0.1
        loop_count = int((expected_seconds + group_duration - 0.0001) // group_duration)
        result["loop_counts"].append(loop_count)

        start_freq = freq_params[0] + 10
        end_freq = freq_params[1] + 10
        change_type = freq_params[3]

        frequency_sequence = []
        combined_sequence = []

        if change_type == 1 or change_type == 4:
            fixed_freq = start_freq
            total_points = len(intensities) * loop_count
            frequency_sequence = [fixed_freq] * total_points
            for i in range(total_points):
                current_intensity = intensities[i % len(intensities)]
                next_intensity = intensities[(i + 1) % len(intensities)] if i < total_points - 1 else intensities[0]
                intensity_range = create_value_range(current_intensity, next_intensity, range_steps)
                freq_range = (fixed_freq,) * range_steps
                combined_sequence.append((freq_range, intensity_range))
        elif change_type == 2:
            for loop_idx in range(loop_count):
                for i in range(len(intensities)):
                    progress = i / (len(intensities) - 1) if len(intensities) > 1 else 0
                    current_freq = start_freq + (end_freq - start_freq) * progress
                    freq_val = int(round(current_freq))
                    frequency_sequence.append(freq_val)
            for i in range(len(frequency_sequence)):
                current_freq_val = frequency_sequence[i]
                current_intensity = intensities[i % len(intensities)]
                next_intensity = intensities[(i + 1) % len(intensities)] if i < len(frequency_sequence) - 1 else intensities[0]
                intensity_range = create_value_range(current_intensity, next_intensity, range_steps)
                next_freq = frequency_sequence[(i + 1) % len(frequency_sequence)] if i < len(frequency_sequence) - 1 else frequency_sequence[0]
                freq_range = create_value_range(current_freq_val, next_freq, range_steps)
                combined_sequence.append((freq_range, intensity_range))
        elif change_type == 3:
            total_points = len(intensities) * loop_count
            for i in range(total_points):
                progress = i / (total_points - 1) if total_points > 1 else 0
                current_freq = start_freq + (end_freq - start_freq) * progress
                freq_val = int(round(current_freq))
                frequency_sequence.append(freq_val)
            for i in range(total_points):
                current_freq_val = frequency_sequence[i]
                current_intensity = intensities[i % len(intensities)]
                next_intensity = intensities[(i + 1) % len(intensities)] if i < total_points - 1 else intensities[0]
                intensity_range = create_value_range(current_intensity, next_intensity, range_steps)
                next_freq = frequency_sequence[(i + 1) % len(frequency_sequence)] if i < total_points - 1 else frequency_sequence[0]
                freq_range = create_value_range(current_freq_val, next_freq, range_steps)
                combined_sequence.append((freq_range, intensity_range))

        result["frequency_sequences"].append(frequency_sequence)
        result["combined_sequences"].append(combined_sequence)
        all_section_sequences.extend(combined_sequence)

    # 添加休息时间
    rest_time_points = 2
    rest_freq = 0
    rest_intensity = 0
    rest_sequence = []
    for i in range(rest_time_points):
        freq_range = (rest_freq,) * range_steps
        intensity_range = (rest_intensity,) * range_steps
        rest_sequence.append((freq_range, intensity_range))

    final_sequence = all_section_sequences + rest_sequence
    result["final_sequence"] = final_sequence
    return result