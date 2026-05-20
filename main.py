from src import check_config, Graph


def main() -> None:
    try:
        config = check_config()
        graph = Graph()
        graph.start_sim(config)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
