suppressMessages(library(tidyverse))
library(ggplot2)

args = commandArgs(trailingOnly = TRUE)
no.ext <- str_sub(basename(args[1]), end = -5)
out.dir <- dirname(args[1])

data <- read_csv(args[1]) %>%
  gather(key = 'Well', value = 'Fluorescence', -Sample, -`Time (s)`) %>%
  drop_na() %>%
  mutate(Fluorescence = as.double(Fluorescence), Phase = factor(data$Sample, levels = unique(data$Sample)))

first.phase <- levels(data$Phase)[1]
last.phase <- levels(data$Phase)[length(levels(data$Phase))]

data <- data %>% 
  group_by(Well) %>%
  mutate(Normalized_Fluorescence = (Fluorescence - mean(Fluorescence[Phase == last.phase]))/ (mean(Fluorescence[Phase == first.phase]) - mean(Fluorescence[Sample == last.phase]))) %>% 
  ungroup()

sample_data <- data %>% 
  select(Phase, `Time (s)`) %>% 
  group_by(Phase) %>% 
  summarise(min = min(`Time (s)`), max = max(`Time (s)`))

data %>%
  ggplot() +
  geom_line(aes(x = `Time (s)`, y = Normalized_Fluorescence, color = Well)) +
  geom_rect(data = sample_data, ymin = -Inf, ymax = Inf, aes(xmin = min, xmax = max, fill = Phase), alpha = 0.05) +
  theme_light() +
  scale_color_viridis_d() +
  scale_fill_viridis_d() +
  labs(x = 'Time (s)', y = 'Normalized Fluorescence') +
  scale_y_continuous(breaks = seq(0, 1, by = 0.2)) +
  scale_x_continuous(breaks = seq(0, 3000, by = 100))
ggsave(filename = file.path(out.dir, paste('plot_', no.ext, '.pdf', sep = '')), width = 6, height = 4)
