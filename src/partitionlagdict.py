class PartitionLagDict:
    from partitionlag import PartitionLag

    # _partitionLags = {}

    def __init__(self):
        self._partitionLags = {}
        self._lastNitems = []


    def addPartitionLag(self, partitionLag):
        self._partitionLags[partitionLag.partition] = partitionLag.lag
        
        totalLag = self.getTotalLag()
        self._lastNitems.append(totalLag)
        if len(self._lastNitems) > 1000:
            self._lastNitems.pop(0)

    def getAverageLag(self, lastX):
        lengthToUse = len(self._lastNitems)
        if(lastX < lengthToUse):
            lengthToUse = lastX 
        return (sum(self._lastNitems[len(self._lastNitems)-lengthToUse:len(self._lastNitems)])) / lengthToUse

    def getTotalLag(self):
        count = 0
        total = 0
        for _, value in self._partitionLags.items():
            total = total + value
            count = count + 1

        return total

    def toString(self):
        result = "total lag: " + str(self.getTotalLag()) + "\n"
        result += "average lag (last 10): " + str(self.getAverageLag(10)) + "\n"
        for key, value in self._partitionLags.items():
            result = result + "partition: " + str(key) + ", lag: " + str(value) + "\n"
        return result

