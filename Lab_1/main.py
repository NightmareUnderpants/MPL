import random
import csv
import os
import statistics
from collections import defaultdict
from typing import Dict, Tuple, List
from concurrent.futures import ProcessPoolExecutor

CATEGORY_LIST = ['A','B','C','D']

def generate_rand_float():
    return random.random()

def generate_rand_category():
    return CATEGORY_LIST[random.randrange(len(CATEGORY_LIST))]

def generate_csv_file(file_path: str, rowcount: int):
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        datawriter = csv.writer(csvfile, delimiter=' ',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for i in range(rowcount):
            row = [generate_rand_category(), str(generate_rand_float())]
            datawriter.writerow(row)

        return

def process_file(filename: str) -> Dict[str, Tuple[float, float]]:
    try:
        data = defaultdict(list)

        with open(filename, 'r', encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile, delimiter=' ')
            for row in reader:
                if len(row) < 2:
                    continue
                category = row[0]
                value = float(row[1])
                data[category].append(value)

        result = {}
        for category, values in data.items():
            if len(values) == 0:
                continue
            elif len(values) == 1:
                median = values[0]
                stdev = 0.0
            else:
                median = statistics.median(values)
                stdev = statistics.stdev(values)
            result[category] = (median, stdev)

        return result

    except Exception as e:
        print(f"Error: {e} in file {filename}")
        return {}  # Return empty dict instead of None


def process_files_parallel(file_list: List[str]) -> Dict[str, List[Tuple[float, float]]]:
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(process_file, file_list))

    combined_results = defaultdict(list)

    for file_result in results:
        if file_result is not None:
            for category, stats in file_result.items():
                combined_results[category].append(stats)

    return combined_results


def save_results_to_files(combined_results: Dict[str, List[Tuple[float, float]]],
                          original_files: List[str]) -> None:
    for i, filename in enumerate(original_files):
        try:
            base_name = os.path.splitext(filename)[0]
            results_filename = f"{base_name}.csv"

            with open(results_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)

                for category in combined_results:
                    stats_list = combined_results[category]
                    if i < len(stats_list):
                        median, stdev = stats_list[i]
                        writer.writerow([
                            category,
                            f"{median:.6f}",
                            f"{stdev:.6f}"
                        ])
                    else:
                        writer.writerow([category, "0.000000", "0.000000"])

            print(f"Results saved to: {results_filename}")

        except Exception as e:
            print(f"Error saving results for {filename}: {e}")


def process_final_results(combined_results: Dict[str, List[Tuple[float, float]]]) -> None:
    final_data = []

    print()

    for category in combined_results:
        stats_list = combined_results[category]
        medians = [median for median, stdev in stats_list]

        if len(medians) >= 2:
            median_of_medians = statistics.median(medians)
            stdev_of_medians = statistics.stdev(medians)
        elif len(medians) == 1:
            median_of_medians = medians[0]
            stdev_of_medians = 0.0
        else:
            median_of_medians = 0.0
            stdev_of_medians = 0.0

        print(f"{category}, {median_of_medians:.6f}, {stdev_of_medians:.6f}")
        final_data.append([category, median_of_medians, stdev_of_medians])

    try:
        with open("result_data.csv", 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(final_data)
        print("\nResult save to file result_data.csv")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # Создаем 5 файлов
    file_path_list = []

    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)

    for i in range(5):
        filename = 'data_' + str(i + 1) + '.csv'
        file_path = os.path.join(data_dir, filename)
        file_path_list.append(filename)

        generate_csv_file(filename, 10)

    # Обрабатываем 5 файлов
    combined_results = process_files_parallel(file_path_list)

    # Сохраняем результат медиан и стандартных отклонений
    save_results_to_files(combined_results, file_path_list)

    # Вычисляем медиану медиан и стандартное отклонение, и выводим результат
    process_final_results(combined_results)
