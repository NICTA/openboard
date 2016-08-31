#   Copyright 2015,2016 NICTA
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import decimal

from widget_def.models import GraphDefinition, GraphDataset, GraphCluster, GraphClusterBase
from widget_data.models import GraphData, DynamicGraphCluster, GraphDatasetData

from interface import LoaderException

def get_graph(widget_url, label, tile_url):
    """Look up a graph by urls."""
    try:
        return GraphDefinition.objects.get(tile__url=tile_url, 
                tile__widget__family__url=widget_url, 
                tile__widget__label=label)
    except GraphDefinition.DoesNotExist:
        raise LoaderException("Graph for tile %s of widget %s:(%s) does not exist"%(tile_url, widget_url, label))

def clear_graph_data(graph, cluster=None, dataset=None, pval=None, clusters=False):
    """Clear all graph data, or partially by cluster or dataset"""
    data = graph.get_data(pval=pval)
    if clusters and not graph.dynamic_clusters:
        raise LoaderException("Graph %s does not use clusters" % graph.tile.url)
    if graph.use_clusters():
        if cluster:
            if clusters:
                raise LoaderException("Cannot delete clusters for Graph %s unless deleting all data" % graph.tile.url)
            if not isinstance(cluster, GraphCluster):
                try:
                    cluster = GraphCluster.objects.get(graph=graph, url=cluster)
                except GraphCluster.DoesNotExist:
                    raise LoaderException("Cluster %s for graph %s does not exist" % (str(cluster), graph.tile.url))
            data = data.filter(cluster=cluster)
        if dataset:
            raise LoaderException("Graph %s uses clusters - cannot delete by dataset" % graph.tile.url)
    elif dataset:
        if not isinstance(dataset, GraphDataset):
            try:
                dataset = GraphDataset.objects.get(graph=graph, url=dataset)
            except GraphDataset.DoesNotExist:
                raise LoaderException("Dataset %s for graph %s does not exist" % (str(cluster), graph.tile.url))
        data = data.filter(dataset=dataset)
        if cluster or clusters:
            raise LoaderException("Graph %s does not use clusters" % graph.tile.url)
    clear_graph_suppdata(graph, pval, dataset, clusters)
    data.delete()

def clear_graph_suppdata(graph, pval=None, dataset=None, clusters=False):
    if dataset is None:
        GraphDatasetData.objects.filter(dataset__graph=graph, param_value=pval).delete()
    else:
        if not isinstance(dataset, GraphDataset):
            try:
                dataset = GraphDataset.objects.get(graph=graph, url=dataset)
            except GraphDataset.DoesNotExist:
                raise LoaderException("Dataset %s for graph %s does not exist" % (str(dataset), graph.tile.url))
        GraphDatasetData.objects.filter(dataset=dataset, param_value=pval).delete()
    if clusters:
        DynamicGraphCluster.objects.filter(graph=graph, param_value=pval).delete()

def set_dataset_override(graph, dataset, display_name, pval=None):
    if not isinstance(dataset, GraphDataset):
        try:
            dataset = GraphDataset.objects.get(graph=graph, url=dataset)
        except GraphDataset.DoesNotExist:
            raise LoaderException("Dataset %s for graph %s does not exist" % (str(cluster), graph.tile.url))
    (dd, created) = GraphDatasetData.objects.get_or_create(dataset=dataset, param_value=pval, defaults={'display_name': display_name})
    if not created:
        dd.display_name = display_name
        dd.save()

def add_graph_dyncluster(graph,label,sort_order, name, hyperlink=None, pval=None):
    if not graph.dynamic_clusters:
        raise LoaderException("Graph %s does not support dynamic clusters" % graph.tile.url)
    if graph.widget().parametisation and not pval:
        raise LoaderException("Graph %s is parametised, but no parametisation value supplied when creating dynamic cluster" % graph.tile.url)
    if not graph.widget().parametisation and pval:
        raise LoaderException("Graph %s is not parametised, but a parametisation value was supplied when creating dynamic cluster" % graph.tile.url)
    cluster = DynamicGraphCluster(graph=graph, param_value=pval, url=label, sort_order=sort_order, label=name, hyperlink=hyperlink)
    try:
        cluster.save()
    except Exception, e:
        raise LoaderException("Add Cluster %s to graph %s failed: %s" % (label, graph.tile.url, unicode(e)))
    return cluster

def add_graph_data(graph, dataset, value, cluster=None, horiz_value=None, pval=None, val_min=None, val_max=None):
    """Add a graph datapoint.

Return the newly created GraphData object on success.

Raise a LoaderException on error, or if the provided arguments are not valid for the graph.
"""
    if not isinstance(dataset, GraphDataset):
        try:
            dataset = GraphDataset.objects.get(graph=graph, url=dataset)
        except GraphDataset.DoesNotExist:
            raise LoaderException("Dataset %s for graph %s does not exist" % (str(dataset), graph.tile.url))
    if dataset.use_error_bars:
        if val_min is None or val_max is None:
            raise LoaderException("Dataset %s for graph %s requires error bar limits" % (dataset.url, graph.tile.url))
    else:
        if val_min is not None or val_max is not None:
            raise LoaderException("Dataset %s for graph %s does not use error bars" % (dataset.url, graph.tile.url))
    value = decimal.Decimal(value).quantize(decimal.Decimal("0.0001"), rounding=decimal.ROUND_HALF_UP)
    gd = GraphData(graph=graph, param_value=pval, dataset=dataset,value=value, err_valmin=val_min, err_valmax=val_max)
    if graph.use_clusters():
        if not cluster:
            raise LoaderException("Must supply cluster for data for graph %s" % graph.tile.url)   
        elif not isinstance(cluster, GraphClusterBase):
            try:
                cluster = GraphCluster.objects.get(graph=graph, url=cluster)
            except GraphCluster.DoesNotExist:
                raise LoaderException("Cluster %s for graph %s does not exist" % (str(cluster), graph.tile.url))
        if graph.dynamic_clusters:
            gd.dynamic_cluster = cluster
        else:
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

