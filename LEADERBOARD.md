# MLE-bench ELO Leaderboard

ELO ratings across all MLE-bench splits. Sorted by overall performance (All split).

## Methodology

- **Normalized Tournament**: Each agent pair plays exactly 1 game per task (aggregate win rate)
- **Higher-is-Better**: All scores normalized so higher is always better
- **Grand Tournament**: Overall ELO computed across all tasks in the split
- **Initial Rating**: 1500 (standard ELO)
- **K-Factor**: 32

## Splits

| Split | # Tasks | Description |
|-------|---------|-------------|
| **Low (Lite)** | 21 | Low complexity tasks (~158GB) |
| **Medium** | 38 | Medium complexity tasks |
| **High** | 14 | High complexity tasks |
| **MLE-B-30** | 29 | System card evaluation set |
| **All** | 74 | All 75 competitions |

## Rankings

| Rank | Agent | Low (Lite) | Medium | High | MLE-B-30 | All |
|------|-------|------------|--------|------|----------|-----|
| 1 | 🥇 PiEvolve_24hrs | 1620.5 | 1633.8 | 1640.0 | 1635.4 | 1629.8 |
| 2 | 🥈 PiEvolve_12hrs | 1589.2 | 1601.3 | 1615.4 | 1601.3 | 1598.8 |
| 3 | 🥉 Famou-Agent-2.0 | 1551.1 | 1591.2 | 1563.7 | 1588.0 | 1572.9 |
| 4 | deepseek-v3.2-speciale-ML-Master-2.0 | 1534.3 | 1547.1 | 1562.0 | 1551.0 | 1545.2 |
| 5 | Leeroo | 1526.7 | 1581.3 | 1460.1 | 1551.7 | 1541.4 |
| 6 | operand-ensemble | 1530.8 | 1515.9 | 1593.6 | 1551.9 | 1529.8 |
| 7 | MLE-STAR-Pro-1.5 | 1510.0 | 1521.8 | 1509.7 | 1500.8 | 1515.7 |
| 8 | Famou-Agent | 1497.8 | 1525.1 | 1485.3 | 1529.5 | 1509.2 |
| 9 | Thesis | 1466.8 | 1505.2 | 1504.0 | 1516.4 | 1492.0 |
| 10 | AIRA-dojo | 1504.5 | 1485.1 | 1480.5 | 1486.2 | 1491.2 |
| 11 | MLE-STAR-Pro-1.0 | 1506.5 | 1457.0 | 1504.1 | 1473.8 | 1482.4 |
| 12 | gpt-5-R&D-Agent | 1507.5 | 1453.7 | 1478.7 | 1459.6 | 1480.3 |
| 13 | deepseek-r1-InternAgent | 1498.4 | 1468.9 | 1457.2 | 1471.2 | 1477.1 |
| 14 | deepseek-r1-ML-Master | 1464.7 | 1450.8 | 1454.4 | 1431.9 | 1455.6 |
| 15 | multi-agent-Neo | 1435.4 | 1464.6 | 1425.0 | 1445.0 | 1449.4 |
| 16 | o3-gpt-4.1-R&D-Agent | 1458.9 | 1426.4 | 1468.7 | 1420.1 | 1444.2 |
| 17 | o1-preview-R&D-Agent | 1440.5 | 1408.8 | 1437.1 | 1416.3 | 1425.0 |
| 18 | extratime-gpt4o-aide | 1356.1 | 1361.9 | 1360.5 | 1369.8 | 1359.9 |

## Statistics

### Top 3 per Split

**Low (Lite):**
🥇 PiEvolve_24hrs: 1620.55
🥈 PiEvolve_12hrs: 1589.18
🥉 Famou-Agent-2.0: 1551.12

**Medium:**
🥇 PiEvolve_24hrs: 1633.83
🥈 PiEvolve_12hrs: 1601.31
🥉 Famou-Agent-2.0: 1591.23

**High:**
🥇 PiEvolve_24hrs: 1639.99
🥈 PiEvolve_12hrs: 1615.40
🥉 operand-ensemble: 1593.62

**MLE-B-30:**
🥇 PiEvolve_24hrs: 1635.42
🥈 PiEvolve_12hrs: 1601.30
🥉 Famou-Agent-2.0: 1587.98

**All:**
🥇 PiEvolve_24hrs: 1629.79
🥈 PiEvolve_12hrs: 1598.80
🥉 Famou-Agent-2.0: 1572.87

### Most Consistent Agents

Agents appearing in top 10 across multiple splits:

- **PiEvolve_24hrs**: 5/5 splits (Low (Lite), Medium, High, MLE-B-30, All)
- **PiEvolve_12hrs**: 5/5 splits (Low (Lite), Medium, High, MLE-B-30, All)
- **Famou-Agent-2.0**: 5/5 splits (Low (Lite), Medium, High, MLE-B-30, All)
- **deepseek-v3.2-speciale-ML-Master-2.0**: 5/5 splits (Low (Lite), Medium, High, MLE-B-30, All)
- **operand-ensemble**: 5/5 splits (Low (Lite), Medium, High, MLE-B-30, All)
- **MLE-STAR-Pro-1.5**: 5/5 splits (Low (Lite), Medium, High, MLE-B-30, All)
- **AIRA-dojo**: 5/5 splits (Low (Lite), Medium, High, MLE-B-30, All)
- **Leeroo**: 4/5 splits (Low (Lite), Medium, MLE-B-30, All)
- **Famou-Agent**: 4/5 splits (Medium, High, MLE-B-30, All)
- **Thesis**: 4/5 splits (Medium, High, MLE-B-30, All)
- **MLE-STAR-Pro-1.0**: 2/5 splits (Low (Lite), High)
- **gpt-5-R&D-Agent**: 1/5 splits (Low (Lite))

---

*Generated using normalized ELO tournament system*
*Higher ELO = Better performance*
