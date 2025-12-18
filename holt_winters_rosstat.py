def read_data(filename):
    data = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split(';')
            if len(parts) >= 2:
                try:
                    value = float(parts[1].replace(',', '.'))
                    data.append(value)
                except ValueError:
                    continue
    return data


def initial_level_and_trend(data, season_length):
    """
    Начальные значения уровня и тренда
    вычисляются методом наименьших квадратов
    по первому сезонному периоду
    """
    t = list(range(season_length))
    y = data[:season_length]

    t_mean = sum(t) / season_length
    y_mean = sum(y) / season_length

    numerator = sum((t[i] - t_mean) * (y[i] - y_mean) for i in range(season_length))
    denominator = sum((t[i] - t_mean) ** 2 for i in range(season_length))

    trend = numerator / denominator
    level = y_mean - trend * t_mean

    return level, trend


def holt_winters(data, season_length, alpha, beta, gamma):
    level, trend = initial_level_and_trend(data, season_length)

    # Начальные сезонные коэффициенты
    seasonals = [0.0] * season_length
    for i in range(season_length):
        seasonals[i] = data[i] - (level + trend * i)

    # Основной цикл Хольта–Уинтерса
    for t in range(season_length, len(data)):
        last_level = level

        level = alpha * (data[t] - seasonals[t % season_length]) \
                + (1 - alpha) * (level + trend)

        trend = beta * (level - last_level) \
                + (1 - beta) * trend

        seasonals[t % season_length] = gamma * (data[t] - level) \
                + (1 - gamma) * seasonals[t % season_length]

    return level, trend, seasonals


def forecast(level, trend, seasonals, season_length, periods):
    result = []
    for i in range(1, periods + 1):
        value = level + i * trend + seasonals[(i - 1) % season_length]
        result.append(value)
    return result


# =================== ОСНОВНАЯ ПРОГРАММА ===================

data = read_data("rosstat_data.csv")

if len(data) < 24:
    raise ValueError("Для модели Хольта–Уинтерса требуется минимум 2 сезонных периода данных")

season_length = 12  # месяцы

# Коэффициенты сглаживания (можно подбирать)
alpha = 0.4  # уровень
beta = 0.3   # тренд
gamma = 0.3  # сезонность

level, trend, seasonals = holt_winters(
    data,
    season_length,
    alpha,
    beta,
    gamma
)

# Прогноз на полный сезон
forecast_periods = season_length
prediction = forecast(level, trend, seasonals, season_length, forecast_periods)

# =================== ВЫВОД ===================

print("Параметры модели Хольта–Уинтерса:")
print(f"Уровень (a): {level:.4f}")
print(f"Тренд (b): {trend:.4f}")

print("\nСезонные коэффициенты:")
for i, s in enumerate(seasonals, 1):
    print(f"Месяц {i:2d}: {s:.4f}")

print("\nПрогноз на 12 периодов:")
for i, p in enumerate(prediction, 1):
    print(f"Период {i:2d}: {p:.4f}")
