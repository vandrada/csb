#!/usr/bin/env Rscript
library(ggplot2)
library(gridExtra)
library(gtools)

tables <- function(frame) lapply(frame, table)

plot.sample <- function(samp, par) {
  ggplot(samp, aes_string(x=grep(par, colnames(samp), value=T))) +
    geom_bar() + 
    labs(x="Genotype", y="Count", title=par) +
    stat_bin(geom="text", aes(label=..count..), vjust=0.10, hjust=0.0,
                            size=3, colour="red") + 
    theme(legend.position="none", text=element_text(size=6))
}

# from Josh O'Brien at StackOverflow
# https://stackoverflow.com/questions/10706753/
# how-do-i-arrange-a-variable-list-of-plots-using-grid-arrange
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
gt <- read.table("~/Desktop/run2/GT.txt", header=TRUE, fill=TRUE)
headers <- as.list(read.table("~/Desktop/run2/processed.txt", sep="\n"))
colnames(gt) <-
  c("Chromosome", "Position", readLines("~/Desktop/run2/processed.txt"))

# # Create data frames for the individual samples
# # olap data
# c10.olap <- gt[, grep("C10_olap", names(gt), value=TRUE)]
# c258.olap <- gt[, grep("C258_olap", names(gt), value=TRUE)]
# ews.olap <- gt[, grep("EWS_olap", names(gt), value=TRUE)]
# imr90.olap <- gt[, grep("IMR90_olap", names(gt), value=TRUE)]
# t32.olap <- gt[, grep("T32_olap", names(gt), value=TRUE)]
# 
# # et data
# c10.et <- gt[, grep("C10_et", names(gt), value=TRUE)]
# c258.et <- gt[, grep("C258_et", names(gt), value=TRUE)]
# ews.et <- gt[, grep("EWS_et", names(gt), value=TRUE)]
# imr90.et <- gt[, grep("IMR90_et", names(gt), value=TRUE)]
# t32.et <- gt[, grep("T32_et", names(gt), value=TRUE)]
c10 <- gt[, grep("C10", names(gt), value=T)]
c258 <- gt[, grep("C258", names(gt), value=T)]
ews <- gt[, grep("EWS", names(gt), value=T)]
imr <- gt[, grep("IMR90", names(gt), value=T)]
t32 <- gt[, grep("T32", names(gt), value=T)]

# remove the initial data since it can be pretty big
rm(gt)