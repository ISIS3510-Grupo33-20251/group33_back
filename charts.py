import re
import plotly.graph_objs as go
import plotly.io as pio
from collections import Counter
from datetime import datetime

def get_key_url(url):
    if 'flash' in url:
        return 'users flashcards'
    url = url.replace("http://", '').strip()
    response = ''
    split = url.split('/')
    if '.' in "".join(split[1:]):
        return ''

    for i in range(1, len(split), 2):
        response += split[i] + ' '
    return response.strip()

def parse_logs(log_file):
    with open(log_file, "r", encoding = 'latin1') as file:
        logs = file.readlines()
    
    data = []
    for log in logs:
        match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*?Method: (\w+).*?URL: (\S+).*?Response: (\d+)", log)
        if match:
            timestamp, method, url, response = match.groups()
            data.append({
                "timestamp": datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S"),
                "method": method,
                "url": url,
                "response": int(response)
            })
    return data

def generar_graficos():
    translation = {
        "POST": "modification",
        "GET": "lecture",
        "PUT": "modification",
        "DELETE": "deletion"
    }
    log_file = "logs_app.log"
    data = parse_logs(log_file)
    urls = [entry["url"] for entry in data]
    responses = [entry["response"] for entry in data]
    timestamps = [entry["timestamp"] for entry in data]
    methods = [entry["method"] for entry in data]
    
    # Gráfico 1: Código con más fallos (asumiendo fallos como códigos 4xx y 5xx)
    failed_urls = [get_key_url(url) + " " + translation[m] for url, resp, m in zip(urls, responses, methods) if resp >= 400 and get_key_url(url) != '']
    fail_counts = dict(Counter(failed_urls).most_common())  # Convierte en diccionario ordenado
    fig1 = go.Figure(data=[go.Bar(x=list(fail_counts.keys()), y=list(fail_counts.values()))])
    fig1.update_layout(title="Features with the most errors")
    
    # Gráfico 2: Frecuencia de actualización de horarios
    update_patterns = {"daily": 0, "weekly": 0, "monthly": 0}
    pattern = re.compile(r"/schedules/([\w\d]+)[/]?")
    count = {}

    for url, method, response, date in zip(urls, methods, responses,timestamps):
        if "schedules" in url and method == "PUT" and response == 200:
            match = pattern.search(url)
            schedule_id = match.group(1)
            if schedule_id not in count:
                count[schedule_id] = []
            count[schedule_id].append(date)
    for user in count:
        times = count[user]
        for i in range(1, len(times)):
            delta_days = (times[i] - times[i-1]).days

            if delta_days < 2:
                update_patterns["daily"] += 1
            elif delta_days < 8:
                update_patterns["weekly"] += 1
            else:
                update_patterns["monthly"] += 1

    # Create Pie Chart
    fig2 = go.Figure(data=[go.Pie(labels=list(update_patterns.keys()), values=list(update_patterns.values()))])
    fig2.update_layout(title="User Schedule Update Frequency")
    
    # Gráfico 3: Funcionalidades menos usadas
    usage_counts = {}
    for url, method, response in zip(urls, methods, responses):
        key = get_key_url(url)
        if  key != '' and response == 200:
            key += " " + translation[method]
            if key not in usage_counts:
                usage_counts[key] = 0
            usage_counts[key] += 1
    least_used = sorted(usage_counts.items(), key=lambda x: x[1])[:5]
    fig3 = go.Figure(data=[go.Bar(x=[x[0] for x in least_used], y=[x[1] for x in least_used])])
    fig3.update_layout(title="Least used features")
    
    # Gráfico 4: Horas de estudio con flashcards
    study_times = [ts.hour for ts, url in zip(timestamps, urls) if "flash" in url]
    fig4 = go.Figure(data=[go.Histogram(x=study_times, nbinsx=24)])
    fig4.update_layout(title="Hour distribution for flashcards")
    # Gráfico 5: Funcionalidad con más tiempo de uso (simplificado contando accesos)
    time_spent = Counter(get_key_url(url) for url in urls if get_key_url(url) != '')
    most_time_spent = sorted(time_spent.items(), key=lambda x: x[1], reverse=True)[:5]
    fig5 = go.Figure(data=[go.Bar(x=[x[0] for x in most_time_spent], y=[x[1] for x in most_time_spent])])
    fig5.update_layout(title="Most used features")

    # Gráfico 6: Subjects más usados en flashcards
    subject_pattern = re.compile(r"/users/[\w\d]+/([\w\d]+)/flash")
    subject_counts = Counter()

    for url in urls:
        match = subject_pattern.search(url)
        if match:
            subject = match.group(1)
            subject_counts[subject] += 1

    fig6 = go.Figure(data=[go.Bar(x=list(subject_counts.keys()), y=list(subject_counts.values()))])
    fig6.update_layout(title="Most used subjects in flashcards")

    # Gráfico 7: Hora más común para programar reuniones
    meeting_hours = [ts.hour for ts, method, url, resp in zip(timestamps, methods, urls, responses)
                     if method == "POST" and "/meetings/" in url and resp == 200]

    fig7 = go.Figure(data=[go.Histogram(x=meeting_hours, nbinsx=24)])
    fig7.update_layout(title="Hours with the most scheduled meetings",
                       xaxis_title="Hour of the day",
                       yaxis_title="Number of meetings scheduled")
    
    # Gráfico 8: Porcentaje de reminders eliminados
    reminder_creates = 0
    reminder_deletes = 0
    
    for url, method, response in zip(urls, methods, responses):
        if "reminders" in url and response == 200:
            if method == "POST":
                reminder_creates += 1
            elif method == "DELETE":
                reminder_deletes += 1
    
    if reminder_creates > 0:
        deletion_percentage = (reminder_deletes / reminder_creates) * 100
        retention_percentage = 100 - deletion_percentage
        

        fig8 = go.Figure(data=[go.Pie(
            labels=['Retained Reminders', 'Deleted Reminders'], 
            values=[retention_percentage, deletion_percentage],
            hole=0.3,  # Donut chart style
            marker_colors=['#4CAF50', '#F44336']  # Green for retained, red for deleted
        )])
        fig8.update_layout(
            title=f"Reminder Retention vs Deletion Rate<br><sub>{reminder_creates} total reminders created</sub>",
            annotations=[dict(text=f'{deletion_percentage:.1f}%<br>Deleted', x=0.5, y=0.5, font_size=16, showarrow=False)]
        )
    else:
        fig8 = go.Figure(data=[go.Pie(
            labels=['No Data'], 
            values=[100],
            marker_colors=['#CCCCCC']
        )])
        fig8.update_layout(title="Reminder Deletion Rate<br><sub>No reminder data available</sub>")

    return [pio.to_html(fig, full_html=False) for fig in [fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8]]
