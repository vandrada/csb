library("ggplot2")

gq <- read.table("~/Desktop/test/GQ.txt", fill=TRUE, header=TRUE)
#gt <- read.table("~/Desktop/test/GT.txt", fill=TRUE, header=TRUE)
#sdp <- read.table("~/Desktop/test/SDP.txt", fill=TRUE, header=TRUE)

# replace './. with -50 (keeps blank fields as NA)
temp <- sapply(gq[3:length(gq)], function(x) as.numeric(gsub('./.', -50, x)))
#temp <- sapply(gq[3:length(gq)], function(x) gsub('\\./\\.', -50, x))
gq[3:length(gq)] <- temp

# extract the chromosomes and build a list of them
chromosomes <- as.data.frame(table(gq$Chromosome))$Var1
chromosomes.data <- list()

for (i in 1:length(chromosomes)) {
  chromosomes.data[[i]] = gq[gq$Chromosome == chromosomes[i], ]
}

# # METHOD 1: plot one sample and one chromosome per graph
# for (i in 1:length(chromosomes.data)) {
#   chr <- chromosomes.data[[i]]
#   samples <- chr[3:length(chromosomes.data[[i]])]
#   # plot ... (the sample and chromosome, alternatively I can just plot the sample)
#   cols <- colnames(samples)
#   for (j in 1:length(cols)) {
#     sample <- chr[colnames(chr) == cols[j]]
#     name <- paste(chr$Chromosome[[1]], ",", colnames(sample)[[1]])
#     
#     ggplot(as.data.frame(table(sample)), aes(x=sample, y=Freq, colour=Freq)) +
#       geom_point() + 
#       labs(x="Value", y="Frequency",
#            title=paste("Genotype Quality (", name, ")")) +
#       theme(axis.text.x=element_text(angle = 90, hjust = 1),
#             text=element_text(size=8))
#     # finally save the graph
#     ggsave(paste(name, "pdf", sep="."))
#   }
# }

# METHOD 2 (plot a whole sample with log transformation)
samples <- colnames(gq[3:length(chromosomes.data[[i]])])
for (i in 1:length(samples)) {
  samp <- as.data.frame(table(gq[colnames(gq) == samples[[i]]]))
  ggplot(as.data.frame(samp), aes(x=as.numeric(Var1), y=Freq)) + geom_point() +
    theme(text=element_text(size=12),
          axis.text.x=element_text(angle=90, hjust=1)) + coord_trans(x="log")
  ggsave(paste(samples[[i]], "pdf", sep="."))
}
# # only one chromosome
# ggplot(chr10, aes(x=Position, y=Sample1)) + geom_point() + 
#   labs(x="Position", y="Value", title="Genotype Quality (chr10)")
# 
# # the whole thing
# ggplot(gq, aes(x=Position, y=Sample1, colour=Chromosome)) + 
#   geom_jitter(alpha=1/3) + 
#   labs(x="Position", y="Value", title="Genotype Quality")
# 
# # facted by chromosome
# ggplot(gq, aes(x=Position, y=Sample1, colour=Chromosome)) + 
#   geom_jitter(alpha=1/3) + 
#   labs(x="Position", y="Value", title="Genotype Quality") +
#   facet_grid(Chromosome ~ .)
# 
# # plus color for value
# ggplot(gq, aes(x=Position, y=Sample1, colour=Sample1)) + 
#   geom_jitter(alpha=1/3) + 
#   labs(x="Position", y="Value", title="Genotype Quality") +
#   facet_grid(Chromosome ~ .)
#
# # plots a whole sample with log transformation
# g <- as.data.frame(table(gq$Sample))
#ggplot(as.data.frame(g), aes(x=as.numeric(Var1), y=Freq)) + geom_point() + 
#  theme(text=element_text(size=16), axis.text.x=element_text(angle=90, hjust=1))
#+ scale_x_continuous(trans=log2_trans())