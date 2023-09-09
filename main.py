import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter, legal
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Зчитуємо дані з CSV файлів
accounts_data = pd.read_csv("accounts.csv")
posts_data = pd.read_csv("posts.csv")
followers_data = pd.read_csv("sources_for_followers.csv")

# Об'єднуємо дані
merged_data = pd.merge(posts_data, accounts_data, left_on='profile_id', right_on='id', how='left')
merged_data = pd.merge(merged_data, followers_data, left_on='_id', right_on='_id', how='left')

# Графік топ-10 коментаторів
top_commenters = merged_data.groupby('username')['comments_count'].sum().nlargest(10)
plt.figure(figsize=(6, 4.5))
top_commenters.plot(kind='bar', rot=45)
plt.xlabel('Users')
plt.ylabel('Number of Comments')
plt.title('Top Commenters')
plt.tight_layout()
plt.savefig("top_commenters.png")

# Графік середньої кількості коментарів за годину
merged_data['created_time'] = pd.to_datetime(merged_data['created_time'])
hourly_data = merged_data.groupby(merged_data['created_time'].dt.hour)['comments_count'].mean()
plt.figure(figsize=(6, 4))
hourly_data.plot(marker='o', linestyle='-')
plt.xlabel('Hour of the Day')
plt.ylabel('Average Number of Comments')
plt.title('Average Number of Comments per Hour')
plt.grid(True)
plt.savefig("time.png")

# Таблиця результатів
mean_comments = posts_data['comments_count'].mean()
std_comments = posts_data['comments_count'].std()
z_threshold = 1.96

merged_data['z_score'] = (merged_data['comments_count'] - mean_comments) / std_comments
merged_data['overperforming'] = merged_data['z_score'] > z_threshold
merged_data['interaction_score'] = merged_data['comments_count'] / merged_data['followers_count']
merged_data['interaction_score'] = merged_data['interaction_score'].round(4)
merged_data['z_score'] = merged_data['z_score'].round(4)
selected_columns = ['id_x', 'username', 'profile_id', 'followers_count', 'comments_count', 'interaction_score', 'overperforming', 'z_score']

# Зменшення ширини стовпців
column_widths = [40, 80, 60, 60, 60, 40, 40, 40]

# Сортування і створення таблиці
table_data = merged_data[selected_columns].sort_values(by='interaction_score', ascending=False)
table = [table_data.columns.values.tolist()] + table_data.values.tolist()
table = Table(table)

# Налаштування стилів для таблиці
table_style = TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), (0.7, 0.7, 0.7)),
    ('TEXTCOLOR', (0, 0), (-1, 0), (1, 1, 1)),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTSIZE', (0, 0), (-1, -1), 7),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
    ('BOTTOMPADDING', (0, 1), (-1, -1), 2),
    ('BACKGROUND', (0, 1), (-1, -1), (0.9, 0.9, 0.9)),
    ('GRID', (0, 0), (-1, -1), 1, (0, 0, 0)),
])
table.setStyle(table_style)


# Створення документу та додавання елементів до нього
doc = SimpleDocTemplate("report.pdf", pagesize=legal)
story = []
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY, fontName='Arial'))

# Додавання заголовка та інформації до документу
title = "Report"
story.append(Paragraph(title, styles["Title"]))
story.append(Spacer(1, 12))
story.append(Paragraph("Chart of the Most Active Commenters:", styles["Heading1"]))
story.append(Paragraph("Account analysis is valuable because it helps identify which users interact with your content most frequently, such as leaving comments.", styles["Heading2"]))
story.append(Spacer(1, 12))
story.append(Image("top_commenters.png"))
story.append(Paragraph("Chart of Average Number of Comments per Hour:", styles["Heading1"]))
story.append(Paragraph("This analysis helps determine the best times of the day to publish content when audience engagement is highest. It's important because different audiences may be active at different times.", styles["Heading2"]))
story.append(Spacer(1, 12))
story.append(Image("time.png"))
story.append(Paragraph("Table of Results:", styles["Heading1"]))
story.append(Paragraph("I use the Z-score to determine how different a specific data point is from the mean in a statistical distribution. This allows me to determine whether the value is statistically different from the average. In my context, I use the Z-score for the number of comments on each post to determine whether this number is statistically different from the average number of comments for all posts. If the Z-score exceeds 1.96 (which corresponds to a 95% confidence interval), then I consider the post successful.", styles["Heading2"]))
story.append(Paragraph("I have also calculated the Interaction Score using this metric to measure how effectively users interact with posts. Interactions such as the number of comments and the number of followers are taken into account.", styles["Heading2"]))
story.append(Spacer(1, 12))
story.append(table)
story.append(PageBreak())

#Збереження звіту
doc.build(story)


