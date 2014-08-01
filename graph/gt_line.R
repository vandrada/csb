# improved
library("ggplot2")
library("gtools")
library("plyr")

melted <- read.table("~/Desktop/test/GT.txt", fill=TRUE, header=T, 
                     na.strings='./.')

# set up the data frame
t32 <- melted[with(melted, grepl("T32", Sample)), ]
t32.olap <- t32[with(t32, grepl("olap", Sample)), ]
control <- t32[with(t32, grepl("0_accepted", Sample)), ]
t32.olap <- rbind(t32.olap, control)
t32.olap <- within(t32.olap, Sample <- factor(Sample, levels=mixedsort(Sample)))

awesome <- count(na.omit(t32.olap), c("Sample", "Value"))

# plot it
ggplot(na.omit(awesome), aes(x=Sample, y=freq, group=Value, color=Value)) +
  geom_line() + labs(x="Hour", y="Count", title="T32 Olaparib Genotype") +
  scale_x_discrete(labels=c("0", "6", "12", "18", "24"))
#ggsave(file="t32_gt.pdf", width=11, height=4.25)
