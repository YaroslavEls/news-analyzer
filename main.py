import threading
import parsers

threads = [
    threading.Thread(
        target=parsers.UkrPravdaParser('https://www.pravda.com.ua/news/date_').run,
        args=('03.05.2024', '05.05.2024')
    ),
    threading.Thread(
        target=parsers.UnianParser('https://www.unian.ua/news/archive/').run,
        args=('03.05.2024', '05.05.2024')
    ),
    threading.Thread(
        target=parsers.TsnParser('https://tsn.ua/news').run,
        args=('03.05.2024', '05.05.2024')
    )
]

for t in threads: 
    t.start()

for t in threads: 
    t.join()
