suppressMessages(library(tidyverse))
library(ggplot2)

args = commandArgs(trailingOnly = TRUE)
no.ext <- str_sub(basename(args[1]), end = -5)
out.dir <- dirname(args[1])

data <- read_csv(args[1]) %>% 
  gather(key = 'Well', value = 'Fluorescence', -Sample, -`Time (s)`) %>% 
  drop_na() %>% 
  group_by(Well) %>% 
  mutate(Normalized_Fluorescence = (Fluorescence - min(Fluorescence))/ (mean(Fluorescence[Sample == 'ACMA']) - min(Fluorescence)))

data %>%
  ggplot(aes(x = `Time (s)`, y = Normalized_Fluorescence, color = Well)) +
  geom_line() +
  theme_light() +
  scale_color_viridis_d() +
  labs(x = 'Time (s)', y = 'Normalized Fluorescence') +
  scale_y_continuous(breaks = seq(0, 1, by = 0.2))
ggsave(filename = file.path(out.dir, paste('plot_', no.ext, '.pdf', sep = '')), width = 6, height = 4)
