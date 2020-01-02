suppressMessages(library(tidyverse))
library(ggplot2)

# 1 Import ----------------------------------------------------------------

data <- read_csv('plates.csv', col_types = cols()) %>%
  gather(key = 'Well', value = 'Fluorescence', -Sample, -`Time (s)`) %>%
  drop_na() %>%
  mutate(Fluorescence = as.double(Fluorescence),
         Phase = factor(.$Sample, levels = unique(.$Sample))) %>%
  separate(Well, into = c('Well', NA), sep = '_') %>%
  group_by(Well, `Time (s)`, Phase) %>%
  summarize(Fluorescence = mean(Fluorescence)) %>%
  ungroup()

# * 1.1 Normalization -----------------------------------------------------

first.phase <- levels(data$Phase)[1]
last.phase <- levels(data$Phase)[length(levels(data$Phase))]

data <- data %>%
  group_by(Well) %>%
  mutate(Normalized_Fluorescence = (Fluorescence)/ (mean(Fluorescence[Phase == first.phase]))) %>%
  gather(key = 'Signal', value = 'Value', Fluorescence, Normalized_Fluorescence) %>%
  ungroup()

# sample_data is used to draw the boxes representing which points belong to which phase
sample_data <- data %>%
  select(Phase, `Time (s)`) %>%
  group_by(Phase) %>%
  summarise(min = min(`Time (s)`), max = max(`Time (s)`))

# 2 Plot ------------------------------------------------------------------

data %>%
  ggplot() +
  geom_line(aes(x = `Time (s)`, y = Value, color = Well), size = 1) +
  geom_rect(data = sample_data, ymin = -Inf, ymax = Inf, aes(xmin = min, xmax = max, fill = Phase), alpha = 0.05) +
  theme_light() +
  scale_color_viridis_d() +
  scale_fill_viridis_d() +
  facet_grid(Signal ~ ., scales = 'free') +
  labs(x = 'Time (s)', y = '') +
  scale_x_continuous(breaks = seq(0, 3000, by = 100)) +
  expand_limits(y = c(0,1))
ggsave(filename = 'plot_plates.pdf', width = 6, height = 6)
