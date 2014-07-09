#!/usr/bin/env Rscript

library(ggplot2)

plot.sample <- function(samp, col.n) {
  temp <- as.data.frame(cut(samp[[col.n]],
                        breaks=c(0.01, 0.02, 0.1, 0.4, 1.0)))
  colnames(temp) <- c("sample")
  ggplot(na.omit(temp), aes_string(x="sample")) +
    geom_bar() + 
    labs(x="Frequency", y="Count", title=colnames(samp)[col.n]) +
    #stat_bin(geom="text", aes(label=..count..), vjust=0.10, hjust=0.0,
    #         size=3, colour="red") + 
    theme(legend.position="none", text=element_text(size=10))
}

freq <- read.table("~/Desktop/run2/FREQ2.txt", header=TRUE, fill=TRUE,
                   na.strings='./.')
colnames(freq) <-
  c("Chromosome", "Position", readLines("~/Desktop/run2/processed.txt"))

# turn percentages to real numbers
freq[3:length(freq)] <- sapply(freq[3:length(freq)],
                               function(x) as.numeric(sub("%", "", x)) / 100)
freq[3:length(freq)] <- as.data.frame(sapply(freq[3:length(freq)], as.numeric))

#for each sample
temp <- as.data.frame(cut(freq[[3]], breaks=(c(0.01, 0.02, 0.1, 0.4, 1.0))))
colnames(temp) <- c("sample")
ggplot(na.omit(temp), aes(x=sample)) + geom_bar() +
  labs(x="Frequency", y="Count")
