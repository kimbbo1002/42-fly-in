from src import check_config, Graph, sim_visual


def main() -> None:
    try:
        config = check_config()
        graph = Graph()
        graph.start_sim(config)
        graph.print_output()
        if graph.bench is False:
            sim_visual(graph)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
