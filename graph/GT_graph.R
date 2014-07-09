#!/usr/bin/env Rscript

library(ggplot2)
library(gridExtra)
library(gtools)

gt.file <- "~/Desktop/run2/GT.txt"
file.names <- "~/Desktop/run2/processed.txt"

# plots a single sample
plot.sample <- function(samp, par) {
  ggplot(na.omit(samp), aes_string(x=grep(par, colnames(samp), value=T))) +
    geom_bar() +
    labs(x="Genotype", y="Count", title=par) +
    stat_bin(geom="text", aes(label=..count..), vjust=0.10, hjust=0.0,
             size=3, colour="red") +
    theme(legend.position="none", text=element_text(size=6))
}
# plots multiple samples
# ** from Josh O'Brien at StackOverflow
# ** https://stackoverflow.com/questions/10706753/how-do-i-arrange-a-variable-list-of-plots-using-grid-arrange
make.plots <- function(df, name) {
  # sort colnames
  gs <- lapply(mixedsort(colnames(df)), FUN=function(x) plot.sample(df, x))
  n <- length(gs)
  nCol <- floor(sqrt(n))
  pdf(paste(name, "pdf", sep="."), width=8, height=11)
  do.call("grid.arrange", c(gs))
  dev.off()
}

# Read in the initial data
gt <- read.table(gt.file, header=TRUE, fill=TRUE, na.string="./.")
colnames(gt) <-
  c("Chromosome", "Position", readLines(file.names))

# create the data for each cell line
c10 <- gt[, grep("C10", names(gt), value=T)]
c258 <- gt[, grep("C258", names(gt), value=T)]
ews <- gt[, grep("EWS", names(gt), value=T)]
imr <- gt[, grep("IMR90", names(gt), value=T)]
t32 <- gt[, grep("T32", names(gt), value=T)]

# remove the initial data since it can be pretty big
rm(gt)

# graph the data
make.plots(c10, "C10")
make.plots(c258, "C258")
make.plots(ews, "EWS")
make.plots(imr, "IMR90")
make.plots(t32, "T32")
