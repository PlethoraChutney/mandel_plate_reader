suppressMessages(library(tidyverse))
library(ggplot2)

# 1 Import ----------------------------------------------------------------

args = commandArgs(trailingOnly = TRUE)
no.ext <- str_sub(basename(args[1]), end = -5)
out.dir <- dirname(args[1])

# R warns about filling NAs in a bunch of rows without this. Since it's something
# that always happens we can suppress warnings so people don't freak out.

old.warn <- getOption('warn')
options(warn = -1)
data <- read_csv(args[1], col_types = cols()) %>%
  gather(key = 'Well', value = 'Fluorescence', -Sample, -`Time (s)`) %>%
  drop_na() %>%
  mutate(Fluorescence = as.double(Fluorescence), 
         Phase = factor(.$Sample, levels = unique(.$Sample))) %>%
  separate(Well, into = c('Well', NA), sep = '_') %>%
  group_by(Well, `Time (s)`, Phase) %>%
  summarize(Fluorescence = mean(Fluorescence)) %>%
  ungroup()
options(warn = old.warn)

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
ggsave(filename = file.path(out.dir, paste('plot_', no.ext, '.pdf', sep = '')), width = 6, height = 6)
