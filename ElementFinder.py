import sys
import requests
import copy
import math
import statistics
import numpy


def main():
    print("\n1. 범위 검색\n2. 최적 원소 검색\n")

    while True:
        mode = input("검색 모드를 선택해주세요: ")

        if mode == "1":
            performRangeSearch()
            break
        elif mode == "2":
            performOptimalElementSearch()
            break
        else:
            continue    


# ----------------------------------------------------------------------------------------------------------------
# Mode 1
def performRangeSearch():
    database = getData()
    conditions = []
    print("------입력가능한 물성 목록------\n\nelectronegativity\nvanDerWaalsRadius\nionizationEnergy\nelectronAffinity\nmeltingPoint\nboilingPoint\ndensity\nstandardState(solid,liquid,gas)\nbondingType(atomic,diatomic,metallic,covalent network)\ngroupblock(nonmetal,noble gas,halogen,metal,alkali metal,alkaline metal,transition metal,post-transition metal,metalloid,lanthanoid,actinoid)\n")
    while True:
        property_name = input("물성을 입력하세요: ")

#사용자에게 입력 가능한 물성 목록을 출력하고, 사용자로부터 검색할 물성을 입력받습니다.
        
        if property_name in ["electronegativity", "vanDerWaalsRadius", "ionizationEnergy", "electronAffinity", "meltingPoint", "boilingPoint", "density"]:
            try:
                min_value = float(input("물성의 최소 값 입력: "))
                max_value = float(input("물성의 최대 값 입력: "))
            except ValueError:
                print("숫자 형식으로 값을 입력해주세요.")
                continue
#물성들 중 숫자(소수점) 형태로 입력 가능한 물성을 입력했을 때, 최소 값과 최대 값을 입력받습니다. 잘못된 값을 입력했을 때 오류메세지를 출력합니다.
            
            conditions.append((property_name, min_value, max_value))
#입력받은 물성과 최소/최대 값을 튜플 형태로 conditions 리스트에 저장합니다.
            
        elif property_name in ["standardState", "bondingType", "groupBlock"]:
            value = input("원하는 값을 입력하세요: ")
            conditions.append((property_name, value))

#물성들 중 문자열 형태로 입력 가능한 물성을 입력했을 때, 문자열을 입력받습니다.
#예를 들어, standardState 를 입력하면, solid, liquid, gas 중 하나를 입력할 수 있습니다.
#입력받은 물성과 값을 튜플 형태로 conditions 리스트에 저장합니다.
            
        else:
            print("잘못된 물성을 입력했습니다.")
            continue
        
        choice = input("추가 입력하시겠습니까? (y/n): ")
        if choice.lower() != 'y':
            break
#y를 입력하면 추가 입력을 받습니다.
        
    matching_symbols = [
        element["symbol"] for element in database
        if all(
            (condition[0] in element) and
            (element[condition[0]] != "") and
            (
                (len(condition) == 2 and element[condition[0]] == condition[1]) or
                (len(condition) == 3 and (condition[1] <= float(element[condition[0]]) <= condition[2]))
            )
            for condition in conditions
        )
    ]
#condition 의 길이가 2인 경우,( (property_name, value)형태로 저장된 경우 ) 물성 값이 입력한 값과 일치하는지 확인합니다.
#condition 의 길이가 3인 경우,( (property_name, min_value, max_value)형태로 저장된 경우 ) 물성 값이 입력한 범위에 속하는지 확인합니다.
    
    print("조건에 부합하는 원소 기호:")
    for symbol in matching_symbols:
        print(symbol)
    print()
#조건에 부합하는 원소 기호를 모두 출력합니다.



# --------------------------------------------------------------------------------------------------------------------
# Mode 2
def performOptimalElementSearch():
    data = getData()
    
    # 원소 특성들 중 숫자로 나타낼 수 있는 것들만 추립니다.
    numericProperties = [property for property, value in data[7].items() if isNumeric(value)]

    # 일부 원소의 일부 특성은 자료가 존재하지 않습니다. (예시: 헬륨의 ionRadius)
    # 해당 데이터값들은 infinity로 설정하여, 그 특성을 포함하여 검색하는 경우 검색 결과에서 제외시킵니다.
    sanitizedData = sanitize(origitalData=data, properties=numericProperties)

    listSearchableProperties(properties=numericProperties)
    searchConditions = getSearchConditions(properties=numericProperties)

    optimalElementIndex = findOptimalElementIndex(data=sanitizedData, conditions=searchConditions)
    displayResult(data[optimalElementIndex])


def isNumeric(value):
    return isinstance(value, int) or isinstance(value, float)


def getData():
    response = requests.get("https://neelpatel05.pythonanywhere.com")

    if response.status_code == 200:
        return response.json()
    else:
        sys.exit("주기율표 데이터를 받아오는 데 실패했습니다.")



def sanitize(origitalData, properties):
    data = copy.deepcopy(origitalData)

    for property in properties:
        for i in range(len(data)):
            if isNumeric(data[i][property]):
                continue
            else:
                data[i][property] = float('inf')

    return data



def listSearchableProperties(properties):
    print("\n\n검색 가능한 특성 목록:")

    for property in properties:
        print("  " + property)

    print("\n")




def getSearchConditions(properties):
    conditions = {}

    while True:
        property = input("목표 특성을 입력해주세요. 아무것도 입력하지 않을 시 현재 조건으로 검색을 진행합니다: ")

        if property == "" and len(conditions) != 0:
            break
        elif property in properties and property not in conditions.keys():
            while True:
                try:
                    value = float(input("목표 값: "))
                    weight = 0

                    while weight <= 0:
                        try:
                            weight = float(input("가중치: "))
                        except ValueError:
                            continue
                    
                    conditions[property] = (value, weight)
                    print("\n현재 조건: ", conditions)
                    break
                except ValueError:
                    continue
    
    return conditions



def findOptimalElementIndex(data, conditions):
    d = numpy.full(len(data), float(0))

    for (property, (targetValue, weight)) in conditions.items():
        # property가 예를 들어 끓는점일 경우, 각 원소에 대해
        # `(해당 원소의 끓는점 - 목표 끓는점) / 모든 원소의 끓는점 표준편차`를 구합니다.
        tmp = map(lambda element: abs((element[property] - targetValue) / stdev(property, data)) * weight, data)
        d += numpy.array(list(tmp))

    return d.argmin()


def stdev(property, data):
    values = list(map(lambda element: element[property], data))
    filteredValues = list(filter(lambda value: math.isfinite(value), values))
    return statistics.stdev(filteredValues)



def displayResult(element):
    print(f"\n🎉 목표 조건에 가장 근접한 특성을 지닌 원소는 {element['name']}입니다!")
    for property, value in element.items():
        print(property, ": ", value, sep="")




main()
