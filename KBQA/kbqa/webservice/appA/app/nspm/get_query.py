from interpreter import process_question


def read_query_output(question):
    query_output = process_question(question)
    return query_output


if __name__ == "__main__":
    output = read_query_output("vilhelm petersen has architected in how many cities?")
    print("vilhelm petersen has architected in how many cities? - ", output)
