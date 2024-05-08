import threading
import parsers

start = '01.05.2023'
end = '01.05.2024'

threads = [
    threading.Thread(
        target=parsers.UkrPravdaParser('https://www.pravda.com.ua/news/date_').run,
        args=(start, end)
    ),
    threading.Thread(
        target=parsers.UnianParser('https://www.unian.ua/news/archive/').run,
        args=(start, end)
    ),
    threading.Thread(
        target=parsers.TsnParser('https://tsn.ua/news').run,
        args=(start, end)
    ),
    threading.Thread(
        target=parsers.RbcParser('https://www.rbc.ua/rus/archive/').run,
        args=(start, end)
    )
]

for t in threads: 
    t.start()

for t in threads: 
    t.join()
