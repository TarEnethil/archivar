function makeMultiSelect(id, selectableHeading, selectionHeading, cssCls, onSelectFunc=undefined, onDelectFunc=undefined) {
var filter = $('<input type="text" class="search-filter" autocomplete="off" placeholder="filter">')
filter.insertAfter("label[for=" + id + "]");
var s = $("#" + id).multiSelect({
    keepOrder: true,
    selectableHeader: selectableHeading,
    selectionHeader: selectionHeading,
    cssClass: cssCls,
    selectableOptgroup: true,
    afterInit: function(ms){
        var searchString = '#' + this.$container.attr('id')+' .ms-elem-selectable:not(.ms-selected)'
        searchString += ', #' + this.$container.attr('id')+' .ms-elem-selection.ms-selected';
        this.filt = filter.quicksearch(searchString)
    },
    afterSelect: function(value) {
        this.filt.cache();

        if (onSelectFunc != undefined) {
            onSelectFunc(value);
        }
    },
    afterDeselect: function(value) {
        this.filt.cache();

        if (onDelectFunc != undefined) {
            onDelectFunc(value);
        }
    }
});

return s;
}