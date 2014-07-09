#!/usr/bin/env Rscript

library(ggplot2)
library(gridExtra)
library(gtools)

freq.file <- "~/Desktop/run2/FREQ2.txt"
file.names <- "~/Desktop/run2/processed.txt"

# plots a single sample
plot.sample <- function(samp, par) {
  temp <- as.data.frame(cut(samp[[grep(par, colnames(samp), value=TRUE)]],
                        breaks=c(0.0, 0.01, 0.02, 0.1, 0.4, 1.0)))
  colnames(temp) <- c("sample")
  ggplot(na.omit(temp), aes_string(x="sample")) +
    geom_bar() +
    labs(x="Frequency", y="Count", title=par) +
    theme(legend.position="none", text=element_text(size=6))
}

# plots multiple samples
make.plots <- function(df, name) {
  # sort colnames
  gs <- lapply(mixedsort(colnames(df)), FUN=function(x) plot.sample(df, x))
  n <- length(gs)
  nCol <- floor(sqrt(n))
  pdf(paste(name, "pdf", sep="."), width=11, height=8)
  do.call("grid.arrange", c(gs))
  dev.off()
}

freq <- read.table(freq.file, header=TRUE, fill=TRUE, na.strings='./.')
colnames(freq) <- c("Chromosome", "Position", readLines(file.names))

# turn percentages to real numbers
freq[3:length(freq)] <- sapply(freq[3:length(freq)],
                               function(x) as.numeric(sub("%", "", x)) / 100)
freq[3:length(freq)] <- as.data.frame(sapply(freq[3:length(freq)], as.numeric))

# plot...
# create the data for each cell line
c10 <- freq[, grep("C10", names(freq), value=T)]
c258 <- freq[, grep("C258", names(freq), value=T)]
ews <- freq[, grep("EWS", names(freq), value=T)]
imr <- freq[, grep("IMR90", names(freq), value=T)]
t32 <- freq[, grep("T32", names(freq), value=T)]

# remove the initial data since it can be pretty big
rm(freq)

# graph the data
make.plots(c10, "C10")
make.plots(c258, "C258")
make.plots(ews, "EWS")
make.plots(imr, "IMR90")
make.plots(t32, "T32")
