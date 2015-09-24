import decimal

from widget_def.models import GraphDefinition, GraphDataset, GraphCluster
from widget_data.models import GraphData

from interface import LoaderException

def get_graph(widget_url, actual_location_url, actual_frequency_url, tile_url):
    """Look up a graph by urls."""
    try:
        return GraphDefinition.objects.get(tile__url=tile_url, 
                tile__widget__family__url=widget_url, 
                tile__widget__actual_location__url=actual_location_url,
                tile__widget__actual_frequency__url=actual_frequency_url)
    except GraphDefinition.DoesNotExist:
        raise LoaderException("Graph for tile %s of widget %s:(%s,%s) does not exist"%(tile_url, widget_url, actual_location_url, actual_frequency_url))

def clear_graph_data(graph, cluster=None, dataset=None):
    """Clear all graph data, or partially by cluster or dataset"""
    data = graph.get_data()
    if graph.use_clusters():
        if cluster:
            if not isinstance(cluster, GraphCluster):
                try:
                    cluster = GraphCluster.objects.get(graph=graph, url=cluster)
                except GraphCluster.DoesNotExist:
                    raise LoaderException("Cluster %s for graph %s does not exist" % (str(cluster), graph.tile.url))
            data = data.filter(cluster=cluster)
        elif cluster:
            raise LoaderException("Graph %s does not use clusters" % graph.tile.url)
        if dataset:
            raise LoaderException("Graph %s uses clusters - cannot delete by dataset" % graph.tile.url)
    elif dataset:
        if not isinstance(dataset, GraphDataset):
            try:
                dataset = GraphDataset.objects.get(graph=graph, url=dataset)
            except GraphDataset.DoesNotExist:
                raise LoaderException("Dataset %s for graph %s does not exist" % (str(cluster), graph.tile.url))
        data = data.filter(dataset=dataset)
        if cluster:
            raise LoaderException("Graph %s does not use clusters" % graph.tile.url)
    data.delete()

def add_graph_data(graph, dataset, value, cluster=None, horiz_value=None):
    """Add a graph datapoint.

Return the newly created GraphData object on success.

Raise a LoaderException on error, or if the provided arguments are not valid for the graph.
"""
    if not isinstance(dataset, GraphDataset):
        try:
            dataset = GraphDataset.objects.get(graph=graph, url=dataset)
        except GraphDataset.DoesNotExist:
            raise LoaderException("Dataset %s for graph %s does not exist" % (str(dataset), graph.tile.url))
    value = decimal.Decimal(value).quantize(decimal.Decimal("0.0001"), rounding=decimal.ROUND_HALF_UP)
    gd = GraphData(graph=graph, dataset=dataset,value=value)
    if graph.use_clusters():
        if not cluster:
            raise LoaderException("Must supply cluster for data for graph %s" % graph.tile.url)   
        elif not isinstance(cluster, GraphCluster):
            try:
                cluster = GraphCluster.objects.get(graph=graph, url=cluster)
            except GraphCluster.DoesNotExist:
                raise LoaderException("Cluster %s for graph %s does not exist" % (str(cluster), graph.tile.url))
        gd.cluster = cluster
    else:
        if graph.horiz_axis_type == graph.NUMERIC:
            gd.horiz_numericval = decimal.Decimal(horiz_value).quantize(decimal.Decimal("0.0001"), rounding=decimal.ROUND_HALF_UP)
        elif graph.horiz_axis_type == graph.DATE:
            gd.horiz_dateval = horiz_value
        elif graph.horiz_axis_type == graph.TIME:
            gd.horiz_timeval = horiz_value
        elif graph.horiz_axis_type == graph.DATETIME:
            gd.horiz_dateval = horiz_value.date()
            gd.horiz_timeval = horiz_value.time()
    gd.save()
    return gd

