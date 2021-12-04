import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import power_grid as grid


# Import data
data = grid.import_data()


# Compute new measures
data.hourly['Förbrukning'] = (data.hourly['Timmättförbr exkl. avk.last']
                             + data.hourly['Ospec. förbrukning']
                             + data.hourly['Avkopplingsb. last']
                             + data.hourly['Schablonleverans förbrukning']
                             + data.hourly['Schablonleverans förluster'])

data.hourly['Produktion'] = (data.hourly['Vattenkraft produktion']
                             + data.hourly['Solkraft produktion']
                             + data.hourly['Vindkraft produktion']
                             + data.hourly['Kärnkraft produktion'])


xlim = [pd.Timestamp('2011-01-01'), pd.Timestamp('2021-01-01')]

# ----- Produktion
fig = plt.figure()
ax = plt.subplot(111)
ax.plot(data.hourly['Tid'], data.hourly['Vattenkraft produktion'], alpha=0.5)
ax.plot(data.daily['Tid'], data.daily['Vattenkraft produktion'], alpha=0.5)
ax.plot(data.monthly['Tid'], data.monthly['Vattenkraft produktion'], alpha=0.5)
ax.set_xlim(xlim)
ax.set_ylabel('Produktion (MW)')
plt.show()


# ----- Årlig Produktion
fig = plt.figure()
ax = plt.subplot(111)
ax.plot(data.monthly['Tid'], data.monthly_sum['Vattenkraft produktion']/1e6, alpha=0.5)
ax.set_xlim(xlim)
ax.set_ylabel('Producerad (TWh/månad)')
plt.show()


# ----- Produktion
fig = plt.figure()
ax = plt.subplot(111)
x = data.hourly['Tid']
ax.plot(x, data.hourly['Vattenkraft produktion'], alpha=0.5)
ax.plot(x, data.hourly['Solkraft produktion'], alpha=0.5)
ax.plot(x, data.hourly['Vindkraft produktion'], alpha=0.5)
ax.plot(x, data.hourly['Kärnkraft produktion'], alpha=0.5)
# ax.plot(x, data.hourly['Vattenkraft'])
# ax.plot(x, data.hourly['Solkraft'])
# ax.plot(x, data.hourly['Vindkraft'])
# ax.plot(x, data.hourly['Kärnkraft'])
ax.plot(x, -(data.hourly['Timmättförbr exkl. avk.last']), 'k')
ax.set_xlim(xlim)
ax.set_ylabel('Produktion (MWh)')
plt.show()


# ----- Produktion/Installerad effekt
fig = plt.figure()
ax = plt.subplot(111)
x = data.hourly['Tid']
ax.plot(x, 100 * data.hourly['Vattenkraft produktion'] / data.hourly['Vattenkraft'], alpha=0.5)
ax.plot(x, 100 * data.hourly['Solkraft produktion'] / data.hourly['Solkraft'], alpha=0.5)
ax.plot(x, 100 * data.hourly['Vindkraft produktion'] / data.hourly['Vindkraft'], alpha=0.5)
ax.plot(x, 100 * data.hourly['Kärnkraft produktion'] / data.hourly['Kärnkraft'], alpha=0.5)
ax.set_xlim(xlim)
ax.set_ylabel('Produktion/Installerad effekt (%)')
plt.show()


# Produktion/Förbrukning
fig = plt.figure()
ax = plt.subplot(111)
x = data.hourly['Tid']
ax.plot(x, -100 * data.hourly['Vattenkraft produktion'] / data.hourly['Förbrukning'])
ax.plot(x, -100 * data.hourly['Solkraft produktion'] / data.hourly['Förbrukning'])
ax.plot(x, -100 * data.hourly['Vindkraft produktion'] / data.hourly['Förbrukning'])
ax.plot(x, -100 * data.hourly['Kärnkraft produktion'] / data.hourly['Förbrukning'])
ax.plot(x, -100 * data.hourly['Produktion'] / data.hourly['Förbrukning'], 'k')
ax.set_xlim(xlim)
ax.set_ylabel('Produktion/Förbrukning (%)')
plt.show()


# ----- PDF
fig = plt.figure()
ax = plt.subplot(111)
ax.hist(100 * data.hourly['Vattenkraft produktion'] / data.hourly['Vattenkraft'], 1000, alpha=0.5, density=True)
ax.hist(100 * data.hourly['Solkraft produktion'] / data.hourly['Solkraft'], 1000, alpha=0.5, density=True)
ax.hist(100 * data.hourly['Vindkraft produktion'] / data.hourly['Vindkraft'], 1000, alpha=0.5, density=True)
ax.hist(100 * data.hourly['Kärnkraft produktion'] / data.hourly['Kärnkraft'], 1000, alpha=0.5, density=True)
ax.set_xlim([0, 110])
ax.set_ylim([0, 0.1])
ax.set_xlabel('Power/Installed Power (%)')
ax.set_ylabel('PDF')
plt.show()


# ----- CDF
fig = plt.figure()
ax = plt.subplot(111)
ax.hist(100 * data.hourly['Vattenkraft produktion'] / data.hourly['Vattenkraft'], 1000, alpha=0.5, density=True, cumulative=True)
ax.hist(100 * data.hourly['Solkraft produktion'] / data.hourly['Solkraft'], 1000, alpha=0.5, density=True, cumulative=True)
ax.hist(100 * data.hourly['Vindkraft produktion'] / data.hourly['Vindkraft'], 1000, alpha=0.5, density=True, cumulative=True)
ax.hist(100 * data.hourly['Kärnkraft produktion'] / data.hourly['Kärnkraft'], 1000, alpha=0.5, density=True, cumulative=True)
ax.set_xlim([0, 110])
# ax.set_ylim([0, 1])
ax.set_xlabel('Power/Installed Power (%)')
ax.set_ylabel('CDF')
plt.show()
